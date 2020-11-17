###########################################################
# GE SRTP PLC Low level library
#
# Author: Collin Matthews - 2020
###########################################################

import os, sys
import re
import struct



class GeSrtp:


    #Public Functions
    def __init__(self):

        self.PLC_PORT = 18245

        # Exploit paper does not show it, but first send 56 bytes of
        # all 0s to the PLC before real message. It will respond with
        # 01 00 ......
        self.INIT_MSG = bytearray(56)

        # Example Transmit message.
        # This is standard message format, you need to
        # update some fields before sending.
        self.BASE_MSG = [
            b'\x02',        # 00 - Type (03 is Return, 02 is Transmit)
            b'\x00',        # 01 - Reserved/Unknown
            b'\x06',        # 02 - Seq Number - FILL AT RUNTIME
            b'\x00',        # 03 - Reserved/Unknown
            b'\x00',        # 04 - Text Length - FILL AT RUNTIME ???
            b'\x00',        # 05 - Reserved/Unknown
            b'\x00',        # 06 - Reserved/Unknown
            b'\x00',        # 07 - Reserved/Unknown
            b'\x00',        # 08 - Reserved/Unknown
            b'\x01',        # 09 - Reserved/Unknown*
            b'\x00',        # 10 - Reserved/Unknown
            b'\x00',        # 11 - Reserved/Unknown
            b'\x00',        # 12 - Reserved/Unknown
            b'\x00',        # 13 - Reserved/Unknown
            b'\x00',        # 14 - Reserved/Unknown
            b'\x00',        # 15 - Reserved/Unknown
            b'\x00',        # 16 - Reserved/Unknown
            b'\x01',        # 17 - Reserved/Unknown*
            b'\x00',        # 18 - Reserved/Unknown
            b'\x00',        # 19 - Reserved/Unknown
            b'\x00',        # 20 - Reserved/Unknown
            b'\x00',        # 21 - Reserved/Unknown
            b'\x00',        # 22 - Reserved/Unknown
            b'\x00',        # 23 - Reserved/Unknown
            b'\x00',        # 24 - Reserved/Unknown
            b'\x00',        # 25 - Reserved/Unknown
            b'\x00',        # 26 - Time Seconds - FILL AT RUNTIME
            b'\x00',        # 27 - Time Minutes - FILL AT RUNTIME
            b'\x00',        # 28 - Time Hours   - FILL AT RUNTIME
            b'\x00',        # 29 - Reserved/Unknown
            b'\x06',        # 30 - Seq Number (Repeated) - FILL AT RUNTIME ???? 0x06 always?
            b'\xc0',        # 31 - Message Type
            b'\x00',        # 32 - Mailbox Source
            b'\x00',        # 33 - Mailbox Source
            b'\x00',        # 34 - Mailbox Source
            b'\x00',        # 35 - Mailbox Source
            b'\x10',        # 36 - Mailbox Destination
            b'\x0e',        # 37 - Mailbox Destination
            b'\x00',        # 38 - Mailbox Destination
            b'\x00',        # 39 - Mailbox Destination
            b'\x01',        # 40 - Packet Number
            b'\x01',        # 41 - Total Packet Number
            b'\x00',        # 42 - Service Request Code - (Operation Type SERVICE_REQUEST_CODE)
            b'\x00',        # 43 - Request Dependent Space (For Reading: set MEMORY_TYPE_CODE)
            b'\x00',        # 44 - Request Dependent Space (For Reading: set to Address - 1)(LSB)
            b'\x00',        # 45 - Request Dependent Space (For Reading: set to Address - 1)(MSB)
            b'\x00',        # 46 - Request Dependent Space (For Reading: Data Size Bytes)(LSB)
            b'\x00',        # 47 - Request Dependent Space (For Reading: Data Size Bytes)(MSB)
            b'\x00',        # 48 - Reserved/Unknown
            b'\x00',        # 49 - Reserved/Unknown
            b'\x00',        # 50 - Reserved/Unknown
            b'\x00',        # 51 - Reserved/Unknown
            b'\x00',        # 52 - Reserved/Unknown
            b'\x00',        # 53 - Reserved/Unknown
            b'\x00',        # 54 - Reserved/Unknown
            b'\x00'         # 55 - Reserved/Unknown
        ]

        # Used at byte locaiton 42
        self.SERVICE_REQUEST_CODE = {
            "PLC_STATUS"             : b'\x00',
            "RETURN_PROG_NAME"       : b'\x03',
            "READ_SYS_MEMORY"        : b'\x04',    # Used to read general memory register (Example: %R12344)
            "READ_TASK_MEMORY"       : b'\x05',
            "READ_PROG_MEMORY"       : b'\x06',
            "WRITE_SYS_MEMORY"       : b'\x07',
            "WRITE_TASK_MEMORY"      : b'\x08',
            "WRITE_PROG_MEMORY"      : b'\x09',
            "RETURN_DATETIME"        : b'\x25',
            "RETURN_CONTROLLER_TYPE" : b'\x43'
        }

        # Used at byte locaiton 43
        self.MEMORY_TYPE_CODE = {
            "R"  :   b'\x08',    # Register (Word)
            "AI" :   b'\x0a',    # Analog Input (Word)
            "AQ" :   b'\x0c',    # Analog Output (Word)
            "I"  :   b'\x10',    # Descrete Input (Byte)
            "Q"  :   b'\x12',    # Descrete Output (Byte)
        }


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
            tmp = self.BASE_MSG.copy()
            tmp[42] = self.SERVICE_REQUEST_CODE["READ_SYS_MEMORY"]
            # Update for type of register
            tmp[43] = self.MEMORY_TYPE_CODE[re.search('(R|AI|AQ|I|Q)',reg)[0]]
            # 0 based register to read
            address = int(re.search('\d+',reg)[0]) - 1
            tmp[44] = int(address & 255).to_bytes(1,byteorder='big')        # Get LSB of Word
            tmp[45] = int(address >> 8 ).to_bytes(1,byteorder='big')        # Get MSB of Word
            # Update for width
            tmp[46] = b'\x01'               # DANGER - TODO make dynamic for different data types.
            arr = tmp
            #print('Array finalized, len:{}'.format( len(arr)))
            self.printArrDebug(arr)
            return(arr)
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