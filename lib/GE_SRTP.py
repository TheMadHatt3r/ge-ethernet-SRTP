###########################################################
# GE SRTP PLC Low level library
#
# Author: Collin Matthews - 2020
#         Dilpreet Chana - 2024
###########################################################

import os, sys
import re
import struct
import socket
from . import GE_SRTP_Messages
import datetime


###########################################################
# Class to contain result and additional meta data from PLC.
###########################################################
class GeSrtpResponse:


    def __init__(self, response, num_registers=1, debug_logging=False):
        self.num_registers = num_registers
        self.register_result = 0
        self.status_code = 0
        self.status_code_minor = 0
        self.debug_logging = debug_logging

        self.fastDecodeResponseMessage(response)



    def fastDecodeResponseMessage(self, msg):
        try:
            start_byte = 44
            end_byte = start_byte + (2 * self.num_registers)
            self.status_code         = struct.unpack('B', bytes([msg[42]]))[0]
            self.status_code_minor   = struct.unpack('B', bytes([msg[43]]))[0]
            self.register_result     = int.from_bytes(struct.unpack('B' * 2 * self.num_registers, msg[start_byte:end_byte]), byteorder='little')
            if self.debug_logging: 
                print("PLC Status Codes (42,43): 0x{:02x} 0x{:02x}".format(self.status_code, self.status_code_minor))
                print("Data From Reg (hex): ", end="")
                print("".join("{:02x}".format(byte) for byte in msg[start_byte:end_byte]), end="")
                print()

        except Exception as err:
            print("Exception:" + str(err))
            return(None)



###########################################################
# Primary class for communication etc. This class will 
# return a instance of GeSrtpResponse to get results
# from functions like readSysMemory(...)
###########################################################
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
    def initConnection(self, debug_logging=False):
        try:
            print("Connecting to {} on {}... ".format(self.plc_ip, self.PLC_PORT), end='')
            self.plc_sock.connect((self.plc_ip, self.PLC_PORT))
            print("Connected!")

            # Send 56 byte start package.
            print("Sending INIT_MSG to PLC... ", end='')
            if debug_logging:
                print("Full PLC Request: 0x" + ' 0x'.join(format(x, '02x') for x in GE_SRTP_Messages.INIT_MSG))
            self.plc_sock.send(GE_SRTP_Messages.INIT_MSG)
            self.plc_sock.settimeout(2)
            response = self.plc_sock.recv(1024)
            if debug_logging:
                print("Full PLC Response: 0x" + ' 0x'.join(format(x, '02x') for x in response))
            print("OK!")
            #self.printLimitedBin("Response sample from INIT_MSG:",response, end=0)

            # Verify success. (First byte of message is 0x01).
            if response[0] == 1:
                print("Valid Response, Init is good!")
            else:
                print("Failed Init Response check. Expected 0x01, got " + str(response[0]))

            return(0)
        except Exception as err:
            print("\nError making connection to PLC.")
            print("Exception:" + str(err))
            self.plc_sock.close()
            return(1)



    ###########################################################
    # Closes socket connection.
    ###########################################################
    def closeConnection(self):
        try:
            self.plc_sock.close()
        except Exception as err:
            print("Exception:" + str(err))



    ###########################################################
    # Generates command string to send to PLC for reading
    # registers. Expects format of R#### etc.
    # Returns: Bytearray for sending via socket.
    ###########################################################
    def readSysMemory(self, reg, debug_logging=False):
        if not re.search('%*(R|AI|AQ|I|Q|QB|M|MB)\d+',reg):
            raise Exception("Invalid Register Address! (" + reg + ").")

        try:
            # Make copy of generic base message
            tmp = GE_SRTP_Messages.BASE_MSG.copy()
            tmp[42] = GE_SRTP_Messages.SERVICE_REQUEST_CODE["READ_SYS_MEMORY"]
            # Update for type of register
            reg_type = str(re.search('(R|AI|AQ|I|Q|QB|M|MB)',reg)[0])
            tmp[43] = GE_SRTP_Messages.MEMORY_TYPE_CODE[reg_type]
            # 0 based register to read
            address = int(re.search('\d+',reg)[0]) - 1
            if 'B' in reg_type:  # Byte indexing rather than bit indexing
                address //= 8
            tmp[44] = int(address & 255).to_bytes(1,byteorder='big')        # Get LSB of Word
            tmp[45] = int(address >> 8 ).to_bytes(1,byteorder='big')        # Get MSB of Word 

            num_registers = 1
            if ':' in reg:
                num_registers = int(reg.split(':')[1])
            tmp[46] = num_registers.to_bytes(1, byteorder='big')  # Set number of registers to read

            # Set the time bytes
            current_time = datetime.datetime.now().time()
            tmp[26] = current_time.second.to_bytes(1, byteorder='big')
            tmp[27] = current_time.minute.to_bytes(1, byteorder='big')
            tmp[28] = current_time.hour.to_bytes(1, byteorder='big')

            bytes_to_send = b''.join(tmp)
            # Send to PLC, Read Response back as memory value (string type)
            response = self.sendSocketCommand(bytes_to_send, debug_logging)
            return(GeSrtpResponse(response, num_registers, debug_logging))
        except Exception as err:
            print(err)
            raise Exception("Failure reading PLC or Register from PLC. Abort")



    ###########################################################
    # Generates command string to send to PLC for reading
    # time.
    # Returns: Bytearray for sending via socket.
    ###########################################################
    def readDateTime(self):
        try:
            raise Exception("'readDateTime()' Not Yet Implemented.")


            tmp = self.BASE_MSG.copy()
            tmp[42] = self.SERVICE_REQUEST_CODE["RETURN_DATETIME"]
            arr = tmp
            self.printArrDebug(arr)
            return(arr)
        except Exception as err:
            print(err)
            return(None)



###############################################################################
#              ---  ALL METHODS BELOW THIS POINT ARE PRIVATE  ---             #
###############################################################################


    ###########################################################
    # Sends command plc
    # Must first init lib and have open socket.
    # Returns response or throws Exception
    ###########################################################
    def sendSocketCommand(self, msg, debug_logging=False):

        try:
            if not type(msg) == bytes:
                msg = msg.encode()
                print("Warning, msg type not bytes, trying encode... This is a code issue?")
            # print("Sending socket command to PLC... ", end='')
            if debug_logging:
                print("Full PLC Request: 0x" + ' 0x'.join(format(x, '02x') for x in msg))
            self.plc_sock.send(msg)
            self.plc_sock.settimeout(2)
            response = self.plc_sock.recv(1024)
            # print("Response Received!")
            if debug_logging:
                print("Full PLC Response: 0x" + ' 0x'.join(format(x, '02x') for x in response))
            # self.printLimitedBin("PLC Response:", response)
            #self.fastDecodeResponseMessage(response)

            return(response)
        except Exception as err:
            print("\nException:" + str(err))
            # self.plc_sock.close()

        raise Exception("Exception during send/receive of PLC socket. Socket closed, raising...") 



    ###########################################################
    # Decodes message response printing basic info.
    ###########################################################
    # def fastDecodeResponseMessage(self, msg):
    #     try:
    #         status_code         = struct.unpack('B', bytes([msg[42]]))[0]
    #         status_code_minor   = struct.unpack('B', bytes([msg[43]]))[0]
    #         reg_data            = struct.unpack('H', bytearray(msg[44:46]))[0] # Danger, 16 bit word only! TODO
    #         print("")
    #         print("PLC Status Codes (42,43): 0x{:02x} 0x{:02x}".format(status_code, status_code_minor))
    #         print("Data From Reg (hex): {:02x}".format(reg_data))

    #     except Exception as err:
    #         print(err)
    #         return(None)


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