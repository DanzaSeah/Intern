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
# However this script has not integrated connection with OpenPLC, it only starts a Modbus server 
# without any modbus traffic occuring, it only simulates the traffic by changing the value of line_cb 
# in the modbus context every 3 seconds randomly
# If a change is detected, it updates the database to its new value.


# This is location of the line_cb, assuming this is the variable we want to monitor for changes and make changes to the DB
# 1024 voltage, 1025 current, 1026 line_cb
MODBUS_DATA_ADDRESS = 1024
LOCATION_LINE_CB = MODBUS_DATA_ADDRESS + 2
FUNC_NUM = 3  # Function number for holding registers


def establish_connection():
    conn = mysql.connector.connect(
        # localhost if on same ip as database
        host="192.168.192.1",
        user="root",
        password="password",
        database="pandapower_db"
    )
    return conn

# def debug_show_tables(conn):
#     cursor = conn.cursor()
#     cursor.execute("SHOW TABLES;")
#     for row in cursor.fetchall():
#         print(row)

# def debug_show_values(conn):
#     cursor = conn.cursor()
#     cursor.execute("SELECT * from bus_voltage ORDER BY value;")
#     for row in cursor.fetchall():
#         print(row)

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

# To monitor any changes in line_cb and make the update back to the DB
def monitor_modbus(context):
    while True:
        try:
            prev_value = context[0].getValues(FUNC_NUM, LOCATION_LINE_CB, count=1)[0]
            break  # Exit loop once successful
        except IndexError:
            print("Waiting for holding register 102 to be ready...")
            time.sleep(1)

    while True:
        print(f"Monitoring for any changes to line_cb_0 : {prev_value}")
        time.sleep(1)
        current_value = context[0].getValues(FUNC_NUM, LOCATION_LINE_CB, count=1)[0]
        # Compare the value of the line_cb, if it changed, write the changes to the DB
        if current_value != prev_value:
            print("Line_cb value changed!")
            write_breaker_to_db(current_value)
            print(f"Line_cb value updated from {prev_value} to {current_value}")
            prev_value = current_value

# Carry out the update to the DB
def write_breaker_to_db(value):
    conn = establish_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE line_cb SET value = %s WHERE name = 'line_cb_0'", (value,))
    cursor.execute("SELECT value FROM line_cb WHERE name = 'line_cb_0'")
    breaker = int(cursor.fetchone()[0])
    conn.commit()
    conn.close()
    print(f"[DB] Breaker updated to: {breaker}")

# Hardcoded update to the line_cb to simulate a possible change in value in the IED every 3 seconds
def hardcode_update(context):
    while True:
        time.sleep(3)
        new_value = random.randint(0, 1)
        print(f"[Simulated PLC instr] Forcing breaker value to {new_value}")
        context[0].setValues(FUNC_NUM, LOCATION_LINE_CB, [new_value])

# Checks the database every second if there are any values changed, if there is, update the server.
def poll_database_and_update(context):
    prev_values = [None, None, None]  # bus_voltage, current, line_cb

    while True:
        time.sleep(1)  # check every 1 second
        try:
            conn = establish_connection()
            new_values = fetch_ied_data(conn)
            conn.close()

            for i in range(3):
                if new_values[i] != prev_values[i]:
                    context[0].setValues(FUNC_NUM, MODBUS_DATA_ADDRESS + i, [new_values[i]])
                    print(f"[DB Sync] Updated Modbus reg {MODBUS_DATA_ADDRESS} with new value: {new_values[i]}")
                    prev_values[i] = new_values[i]

        except Exception as e:
            print(f"[Error] While polling DB: {e}")


def start_server_and_monitor(register_values):
    print("|| Starting server for PLC to request for data ||")
    block = ModbusSequentialDataBlock(MODBUS_DATA_ADDRESS, [0]*1100)
    store = ModbusSlaveContext(hr=block)
    for i in range(3):
        store.setValues(FUNC_NUM, MODBUS_DATA_ADDRESS, [register_values[i]])

    # The single is set to True for now because we only have one IED
    context = ModbusServerContext(slaves=store, single=True)

    # To identify the IED
    identity = create_identity()

    # Do multi threading to do other operations concurrently with the server

    # To observe any changes and updates can be made to the DB as the server is running
    threading.Thread(target=poll_database_and_update, args=(context,), daemon=True).start()
    threading.Thread(target=monitor_modbus, args=(context,), daemon=True).start()

    # Hardcoded changes to line_cb of the server context as the server is running, 
    # to simulate changes like PLC instructing IED to close the circuit breaker.
    #threading.Thread(target=hardcode_update, args=(context,), daemon=True).start()
    val = context[0].getValues(3, MODBUS_DATA_ADDRESS, count=3)
    print(f"this is the values of context at {MODBUS_DATA_ADDRESS}:{val}")
    # Start server
    StartTcpServer(
        context=context,
        identity=identity,
        address=("0.0.0.0", 5020),
    )

def main():
    conn = establish_connection()
    register_values = fetch_ied_data(conn)
    start_server_and_monitor(register_values)
    conn.close()


if __name__ == '__main__':
    main()


