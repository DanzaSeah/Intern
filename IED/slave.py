import mysql.connector
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSequentialDataBlock,
)


def establish_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="pandapower_db"
    )
    return conn

def debug_show_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    for row in cursor.fetchall():
        print(row)

def debug_show_values(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * from bus_voltage ORDER BY value;")
    for row in cursor.fetchall():
        print(row)

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

# To send sensor/simulation data to the PLC (Modbus Master)
def send_data_with_modbus(register_values):
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, register_values)
    )

    # The single is set to True for now because we only have one IED
    context = ModbusServerContext(slaves=store, single=True)

    # To identify the IED
    identity = create_identity()

    # Start server
    StartTcpServer(
        context,
        identity=identity,
        address=("127.0.0.1", 5020),
    )

def recv_data_with_modbus():
    print("To be completed")

def break_circuit():
    # To simulate the breaking of the circuit
    print("PLA instruction: Break the circuit")

def close_connection(conn):
    conn.close()

def main():
    conn = establish_connection()
    #debug_show_tables(conn)
    register_values = fetch_ied_data
    send_data_with_modbus(register_values)
    conn.close(conn)


if __name__ == '__main__':
    main()