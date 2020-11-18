###########################################################
#
#
# Author: Collin Matthews - 2020
###########################################################

import os, sys

import argparse
from time import sleep
from lib.GE_SRTP import GeSrtp



###########################################################
# MAIN()
###########################################################
def main():


    try:

        plc.initConnection()

        result = plc.readSysMemory(args.reg)

        plc.closeConnection()
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
    plc = GeSrtp(args.plc_ip)

    resp = main()
    sys.exit(resp)