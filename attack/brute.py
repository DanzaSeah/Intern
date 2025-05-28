from pymodbus.client import ModbusTcpClient
import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor

SUBNET = "192.168.192.0/24"
MODBUS_PORT = 502

def check_host(ip):
    try:
        # Quick check if host is up on port 502
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((str(ip), MODBUS_PORT))
        sock.close()
        if result != 0:
            return  # Port closed or host down

        # Send a basic Modbus request
        client = ModbusTcpClient(str(ip), port=MODBUS_PORT)
        connection = client.connect()
        if not connection:
            return

        # Try to read 1 holding register at address 0
        rr = client.read_holding_registers(0, 1, unit=1)
        if rr.isError():
            print(f"{ip}: Modbus error response")
        else:
            print(f"{ip}: Modbus reply received! Data: {rr.registers}")

        client.close()

    except Exception as e:
        print(f"{ip}: Exception occurred - {e}")

# Bruteforce IPs in the subnet
def run_bruteforce():
    ips = list(ipaddress.IPv4Network(SUBNET).hosts())
    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(check_host, ips)

if __name__ == "__main__":
    run_bruteforce()
