import mysql.connector
import threading
import time
import random
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSequentialDataBlock,
)

# This script simulates a Modbus slave IED. 
# It first starts a TCP server for the "PLC" Modbus Master to request data from and to send to. 
# Concurrently, the IED monitors for any changes to the line_cb after being evaluated through sequence 
# of logic and then receiving instruction by the PLC.
# The server can be connected to in OpenPLC using %IW100, %IW101 and %QW100 in ST 
# Slave device configurations:
# Port 5020
# Holding register - read (Start address: 0, Size: 2)
# Holding register - write (Start address: 2, Size: 1)


# 0 voltage, 1 current, 2 line_cb
MODBUS_DATA_ADDRESS = 0
LOCATION_LINE_CB = MODBUS_DATA_ADDRESS + 2
FUNC_NUM_HOLDING_REG = 3  
NUM_REGISTERS_FOR_READING = 3

def establish_connection():
    conn = mysql.connector.connect(
        # localhost if on same ip as database
        host="192.168.192.1",
        user="root",
        password="password",
        database="pandapower_db"
    )
    return conn


def fetch_ied_data(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM bus_voltage WHERE name='bus_voltage_0'")
    voltage = int(cursor.fetchone()[0] * 1000)

    cursor.execute("SELECT value FROM line_current WHERE name='line_current_0'")
    current = int(cursor.fetchone()[0] * 1000)

    cursor.execute("SELECT value FROM line_cb WHERE name='line_cb_0'")
    breaker = int(cursor.fetchone()[0])

    return [voltage, current, breaker]

def create_identity():
    # Device identity
    identity = ModbusDeviceIdentification()
    identity.VendorName = "iTrust"
    identity.ProductName = "Virtual IED"
    identity.ModelName = "IED-MODBUS"
    return identity

# To monitor any changes in line_cb and if it changed, write the changes to the DB
def monitor_modbus(context):
    while True:
        try:
            prev_value = context[0].getValues(FUNC_NUM_HOLDING_REG, LOCATION_LINE_CB, count=1)[0]
            break  # Exit loop once successful
        except IndexError:
            print(f"Waiting for holding register {LOCATION_LINE_CB} to be ready...")
            time.sleep(1)

    while True:
        #print(f"Monitoring for any changes to line_cb_0 : {prev_value}")
        time.sleep(0.5)
        current_value = context[0].getValues(FUNC_NUM_HOLDING_REG, LOCATION_LINE_CB, count=1)[0]
        if current_value != prev_value:
            print("[REG Sync] Line_cb_0 value changed!")
            write_reg_to_db(current_value)
            print(f"[REG Sync] Line_cb_0 DB value updated from {prev_value} to {current_value}")
            prev_value = current_value


# Carry out the update from reg to the DB
def write_reg_to_db(value):
    conn = establish_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE line_cb SET value = %s WHERE name = 'line_cb_0'", (value,))
    conn.commit()
    cursor.execute("SELECT value FROM line_cb WHERE name = 'line_cb_0'")
    reg = int(cursor.fetchone()[0])
 
    conn.close()
    print(f"[DB] Breaker updated to: {reg}")


# Checks the database every second if there are any values changed, if there is, update the server.
def poll_database_and_update(context):
    prev_values = [None, None, None]  # bus_voltage, current, line_cb

    while True:
        time.sleep(0.5)  # check every 1 second
        try:
            conn = establish_connection()
            new_values = fetch_ied_data(conn)
            conn.close()

            for i in range(NUM_REGISTERS_FOR_READING):
                if new_values[i] != prev_values[i]:
                    context[0].setValues(FUNC_NUM_HOLDING_REG, MODBUS_DATA_ADDRESS + i, [new_values[i]])
                    print(f"[DB Sync] Updated Modbus reg {MODBUS_DATA_ADDRESS + i} with new value: {new_values[i]}")
                    prev_values[i] = new_values[i]

        except Exception as e:
            print(f"[Error] While polling DB: {e}")


def start_server_and_monitor(register_values):
    print("|| Starting server for PLC to request for data ||")
    block = ModbusSequentialDataBlock(MODBUS_DATA_ADDRESS, [0]*1100)
    store = ModbusSlaveContext(hr=block)
    for i in range(NUM_REGISTERS_FOR_READING):
        store.setValues(FUNC_NUM_HOLDING_REG, MODBUS_DATA_ADDRESS + i, [register_values[i]])

    # The single is set to True for now because we only have one IED
    context = ModbusServerContext(slaves=store, single=True)

    # To identify the IED
    identity = create_identity()

    # Do multi threading to do other operations concurrently with the server

    # To observe any changes and updates can be made to the DB as the server is running
    threading.Thread(target=poll_database_and_update, args=(context,), daemon=True).start()
    threading.Thread(target=monitor_modbus, args=(context,), daemon=True).start()

    val = context[0].getValues(FUNC_NUM_HOLDING_REG, MODBUS_DATA_ADDRESS, count=3)
    print(f"this is the values of context at {MODBUS_DATA_ADDRESS}:{val}")
    # Start server
    StartTcpServer(
        context=context,
        identity=identity,
        address=("0.0.0.0", 502),
    )

def main():
    conn = establish_connection()
    register_values = fetch_ied_data(conn)
    start_server_and_monitor(register_values)
    conn.close()


if __name__ == '__main__':
    main()


