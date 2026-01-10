###########################################################
# Author: Dilpreet Singh - 2026
###########################################################

from lib.GE_SRTP import *
import time
import json
import builtins

plc_ip = '127.0.0.1'

plc_list = [
    '127.0.108.251',
    '127.0.28.15',
    '127.0.28.17',
    '127.0.28.18',
    '127.0.60.47',
    '127.0.80.1',
    '127.0.80.10',
    '127.0.90.100',
    '127.0.90.101',
    '127.0.90.102',
    '127.0.90.103',
    '127.0.90.106',
    '127.0.90.107',
    '127.0.90.108',
    '127.0.90.109',
    '127.0.90.110',
    '127.0.90.111'
]

# PLC tags
plc_tags = {
    "test1": "R7354",
    "test2": "R5032",
    "test3": "Q00065",
    "test4": "MB03521",
    "test5": "MB03522",
    "test6": "MB03523",
    "test7": "R20000:2",  # NOTE: ADDR:n reads n registers from the addressed register
    "test8": "R20002:2",
    "test9": "R20004:2",
    "test10": "R20006:2",
}

# Buffer print function that logs to a file
def print_and_log(content):
    with open("test-ge.log", "a") as file:
        print(content, file=file, flush=True)
    print(content)

# Function to connect to the PLC
def connect_to_plc(ip):
    plc = GeSrtp(ip)
    plc.initConnection()
    return plc

def parse_tag_data(data, data_type):
    parsed_data = ''
    if data_type == 'int array':
        for d in data:
            parsed_data += chr(d)
    elif data_type == 'byte_string':
        decoded_string = data.decode("utf-8", "ignore")
        parsed_data = ''.join(char for char in decoded_string if char.isprintable())
    else:
        parsed_data = data
    return parsed_data

# Function to read tags from the PLC
def read_tags(plc, tags, debug_logging=False):
    values = {}
    for tag_name, tag_address in tags.items():
        if debug_logging:
            print(f'READING: {tag_address}')
        try:
            res = plc.readSysMemory(tag_address, debug_logging)
        except Exception as e:
            print(f'Failed to read {tag_address}: {e}')
            continue
        if debug_logging:
            print(f'RES: {res.register_result}')
        values[tag_name] = res.register_result
        # if isinstance(values[tag_name], bytes):
        #     values[tag_name] = parse_tag_data(values[tag_name], 'byte_string')
    return values

# Main script
def main():
    debug_logging = False
    check_ip_list = False

    if check_ip_list:
        for p_ip in plc_list:
            plc = connect_to_plc(p_ip, debug_logging)
            try:
                current_values = read_tags(plc, plc_tags, debug_logging)
                print(f'Successfully read value {current_values} from plc ip {plc_ip}')
            except Exception as e:
                print(f'Failed to read from plc ip {plc_ip} with Error: {e}')
        return

    plc = connect_to_plc(plc_ip, debug_logging)
    last_values = {}

    while True:
        try:
            current_values = read_tags(plc, plc_tags)
            curr_ts = int(time.time()*1e3)
            for tag, value in current_values.items():
                if tag not in last_values or last_values[tag] != value:
                    print_and_log(f"{tag} tag '{plc_tags[tag]}' changed to {value} at: {curr_ts}")
            last_values = current_values
            time.sleep(1)
        except KeyboardInterrupt:
            print_and_log("Exiting...")
            break
        except Exception as e:
            print_and_log(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
