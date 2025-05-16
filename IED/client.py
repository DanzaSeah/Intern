import time
from pymodbus.client import ModbusTcpClient
#Supposed to be 0.890, but using 1 to test since bus_voltage_0 is 0.993865 which is more than 0.890 and won't trigger undervoltage
TRIP_VALUE = 1

def fetch_register_values(client):
    start_addr = 99
    count = 3
    rr = client.read_holding_registers(start_addr, count=count)
    assert(rr.function_code < 0x80)     # test that we are not an error
    return rr.registers

def less_than(x, y):
    return x < y

def do_pla_logic(client, register_values, timer_counter, ls_timer_started, last_check_time):
    ### LOAD SHEDDING ###
    [bus_voltage_0, current_0, line_cb_0] = register_values
    if less_than(bus_voltage_0/1000, TRIP_VALUE):
        if not ls_timer_started:
            ls_timer_started = True
            last_check_time = time.time()
    else:
        ls_timer_started = False
        timer_counter = 0

    # Undervoltage
    if ls_timer_started:
        # Each time 1 second has passed under low-voltage condition.
        # print(time.time() - last_check_time)
        if time.time() - last_check_time >= 1:
                    timer_counter += 1
                    last_check_time = time.time()
                    print(f"[Timer] Undervoltage persists for {timer_counter} seconds")

                    if timer_counter == 5:
                        print(">> Opening line_cb_1")

                    if timer_counter == 15:
                        print(">> Opening line_cb_0")
                        client.write_register(101, 1)

    return timer_counter, ls_timer_started, last_check_time

        
def establish_connection():
    address = '127.0.0.1'
    port_num = 5020
    client = ModbusTcpClient(address, port=port_num)
    client.connect()
    return client


def main():
    client = establish_connection()
    timer_counter = 0
    ls_timer_started = False
    last_check_time = time.time()
    while True:
        register_values = fetch_register_values(client)
        timer_counter, ls_timer_started, last_check_time = do_pla_logic(
            client,
            register_values, 
            timer_counter, 
            ls_timer_started, 
            last_check_time
        )
        time.sleep(0.5)
    client.close()


if __name__ == '__main__':
    main()