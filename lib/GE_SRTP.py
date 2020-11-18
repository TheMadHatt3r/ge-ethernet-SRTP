###########################################################
# GE SRTP PLC Low level library
#
# Author: Collin Matthews - 2020
###########################################################

import os, sys
import re
import struct
import socket
from . import GE_SRTP_Messages



class GeSrtp:


    def __init__(self, ip):
        self.PLC_PORT = 18245
        self.plc_ip = ip
        self.plc_sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not ip:
            raise Exception("No IP passed to constructor.")


    def __del__(self):
        try:
            self.plc_sock.close()
        except:
            pass

    ###########################################################
    # Creates inital socket connection,
    # Sends 56 Byte init string to PLC.
    # Returns 0 on ok, else error number.
    ###########################################################
    def initConnection(self):
        try:
            print("Connecting to {} on {}... ".format(self.plc_ip, self.PLC_PORT), end='')
            self.plc_sock.connect((self.plc_ip, self.PLC_PORT))
            print("Connected!")

            # Send 56 byte start package.
            print("Sending INIT_MSG to PLC... ", end='')
            self.plc_sock.send(GE_SRTP_Messages.INIT_MSG)
            self.plc_sock.settimeout(2)
            response = self.plc_sock.recv(1024)
            print("OK!")
            self.printLimitedBin("Response sample from INIT_MSG:",response, end=0)

            # Verify success. (First byte of message is 0x01).
            if response[0] == 1:
                print("Valid Response, Init is good!")
            else:
                print("Failed Init Response check. Expected 0x01, got " + str(response[0]))

            print("")
            return(0)
        except Exception as err:
            print("\nError making connection to PLC.")
            print("Exception:" + str(err))
            self.plc_sock.close()
            return(1)


    def closeConnection(self):
        try:
            self.plc_sock.close()
        except Exception as err:
            print("Exception:" + str(err))



    ###########################################################
    # Sends command plc
    # Must first init lib and have open socket.
    # Returns 0 on ok, else error number.
    ###########################################################
    def sendSocketCommand(self, msg):

        try:
            if not type(msg) == bytes:
                msg = msg.encode()
                print("Warning, msg type not bytes, trying encode... This is a code issue?")
            print("Sending socket command to PLC... ", end='')
            self.plc_sock.send(msg)
            self.plc_sock.settimeout(2)
            response = self.plc_sock.recv(1024)
            print("Response Received!")
            #print("PLC Response: 0x" + ' 0x'.join(format(x, '02x') for x in response))
            self.printLimitedBin("PLC Response:", response)
            self.plc_sock.close()

            self.fastDecodeResponseMessage(response)

            return(0)
        except Exception as err:
            print("Exception:" + str(err))
            self.plc_sock.close()
            return(2)

        return(3)









    ###########################################################
    # Generates command string to send to PLC for reading
    # registers. Expects format of R#### etc.
    # Returns: Bytearray for sending via socket.
    ###########################################################
    def readSysMemory(self, reg):
        if not re.search('%*(R|AI|AQ|I|Q)\d+',reg):
            raise Exception("Invalid Register Address! (" + reg + ").")

        try:
            # Make copy of generic base message
            tmp = GE_SRTP_Messages.BASE_MSG.copy()
            tmp[42] = GE_SRTP_Messages.SERVICE_REQUEST_CODE["READ_SYS_MEMORY"]
            # Update for type of register
            tmp[43] = GE_SRTP_Messages.MEMORY_TYPE_CODE[re.search('(R|AI|AQ|I|Q)',reg)[0]]
            # 0 based register to read
            address = int(re.search('\d+',reg)[0]) - 1
            tmp[44] = int(address & 255).to_bytes(1,byteorder='big')        # Get LSB of Word
            tmp[45] = int(address >> 8 ).to_bytes(1,byteorder='big')        # Get MSB of Word
            # Update for width
            tmp[46] = b'\x01'               # DANGER - TODO make dynamic for different data types.
            #arr = tmp
            #print('Array finalized, len:{}'.format( len(arr)))
            #self.printArrDebug(arr)
            #return(arr)
            bytes_to_send = b''.join(tmp)
            self.sendSocketCommand(bytes_to_send)
        except Exception as err:
            print(err)
            return(None)




            


    ###########################################################
    # Generates command string to send to PLC for reading
    # time.
    # Returns: Bytearray for sending via socket.
    ###########################################################
    def readDateTime(self):
        try:
            tmp = self.BASE_MSG.copy()
            tmp[42] = self.SERVICE_REQUEST_CODE["RETURN_DATETIME"]
            arr = tmp
            self.printArrDebug(arr)
            return(arr)
        except Exception as err:
            print(err)
            return(None)


    ###########################################################
    # Decodes message response printing basic info.
    ###########################################################
    def fastDecodeResponseMessage(self, msg):
        try:
            status_code         = struct.unpack('B', bytes([msg[42]]))[0]
            status_code_minor   = struct.unpack('B', bytes([msg[43]]))[0]
            reg_data            = struct.unpack('H', bytearray(msg[44:46]))[0] # Danger, 16 bit word only! TODO
            print("")
            print("PLC Status Codes (42,43): 0x{:02x} 0x{:02x}".format(status_code, status_code_minor))
            print("Data From Reg (hex): {:02x}".format(reg_data))

        except Exception as err:
            print(err)
            return(None)


    def printArrDebug(self, arr):
        for idx,b in enumerate(arr):
            if idx not in range(6,24):
                print("{:02d}=>0x{:s}".format(idx, b.hex()) )
    

    ###########################################################
    # Prints sample of binary data.
    ###########################################################
    def printLimitedBin(self, pre_msg, msg, start=7, end=7):
        hex_resp_start = ""
        hex_resp_end = ""
        iter_len = sum(1 for _ in enumerate(msg))
        for idx,x in enumerate(msg):
            hex_resp_start += " {:02x}".format(x)
            if idx > start: break
        for idx,x in enumerate(msg):
            if iter_len - idx <= end:
                hex_resp_end += " {:02x}".format(x)
            
        print("{}{}...{} (Only Displaying {} of {} bytes)".format(pre_msg, hex_resp_start, hex_resp_end, start + end, len(msg)))