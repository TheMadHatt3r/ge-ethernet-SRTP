###########################################################
#
#
# Author: Collin Matthews - 2020
###########################################################

import os, sys
import socket
import argparse
from time import sleep
from GE_SRTP import GeSrtp


PLC_PORT = 18245



###########################################################
# Sends command plc
# Returns 0 on ok, else error number.
###########################################################
def sendCommand(msg):
    try:
        TCP_IP = args.plc_ip
        TCP_Port = PLC_PORT

        # Create socket connection.
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_Port))
        sleep(0.1)
        print("Connected to PLC")

        # Send 56 byte start package.
        s.send(plc.INIT_MSG)
        s.settimeout(2)
        response = s.recv(1024)
        print("Init Response Length:" + str(len(response)))
        hex_resp = ""
        for idx,x in enumerate(response):
            hex_resp += " {:02x}".format(x)
            if idx > 9: break
        print("Init Response:{}... (Only Displaying 9 of {} bytes)".format(hex_resp, len(response)))

        # Verify success. (First byte of message is 0x01).
        if response[0] == 1:
            print("Valid Response, Init is good!")
        else:
            print("Failed Init Response check. Expected 0x01, got " + str(response[0]))
    except Exception as err:
        print("Error making connection to PLC.")
        print("Exception:" + err)
        s.close()
        return(1)

    print("")
    # Now send real command and recive real data.
    try:
        if not type(msg) == bytes:
            msg = msg.encode()
            print("Warning, msg type not bytes, trying encode... This is a code issue?")
        print("Sending socket command to PLC... I will wait for response.")
        s.send(msg)
        s.settimeout(3)
        response = s.recv(1024)
        print("PLC Response: 0x" + ' 0x'.join(format(x, '02x') for x in response))
        s.close()

        plc.fastDecodeResponseMessage(response)

        return(0)
    except Exception as err:
        print("Exception:" + err)        
        s.close()
        return(2)

    return(3)








###########################################################
# MAIN()
###########################################################
def main():


    try:

        bytelist = plc.readSysMemory(args.reg)
        bytes_to_send = b''.join(bytelist)
        print(bytes_to_send)
        sendCommand(bytes_to_send)
        print("Done, Exiting...")

    except Exception as err:
        print("High level system exception.")
        print(err)
        return(1)




if __name__ == "__main__":

    # Parse Arguments - Global
    parser = argparse.ArgumentParser(description='GE SRTP PLC Communication Test.')
    parser.add_argument(action="store", dest='plc_ip', help='IP address of PLC')
    parser.add_argument(action="store", dest='reg', help='Register to read or write')
    args = parser.parse_args()

    # Global PLC init
    plc = GeSrtp()

    resp = main()
    sys.exit(resp)