# GE PLC Ethernet Driver - SRTP For Python 3.6+
Turns out GE does not publish this communication protocol anywhere. It is not where to be found on the Internet except a single 2017 security conference paper talking about exploiting GE PLCs in SCADA and Infrastructure systems. 
[Reseach Gate Paper](https://www.researchgate.net/publication/318925679_Leveraging_the_SRTP_protocol_for_over-the-network_memory_acquisition_of_a_GE_Fanuc_Series_90-30). 
Based on the linked paper, which does not give all the required information to start communication, (I had to make use of Wireshark and a GE PLC to figure out there is an initialization step not covered there)
This repo contains a Python library (GE_SRTP) that breaks down the message format for SRTP. It is a fairly simple 56-byte header, with a similar receive structure.

## Work Needed: ##
To date this is basically a proof of concept system. Using this code base, combined with the linked paper above, you can read or write any GE registers. It appears you could even upload or download programs, but that would require extensive testing.

## PLCs Theoretically Supported: ##
 - 90/30
 - 90/70
 - RX3
 - RX7
 - Anything that supports SRTP, which is all Fanuc/Intelligent Platforms stuff?

## Functions: ##
 - Ability to read registers.
 - Ability to write registers. (Not yet implemented)

## Testing Performed: ##
Tested on GE 90/30 and 90/70 Systems with reading of R type registers.

## Requirments: ##
- Python 3.6+ (Regex is the limiting factor for 3.6, with some minor tweaks, you could run earlier 3.x)

## Using the Library: ##
I tried to keep things easy, there are 3 classes, only one of which you need to use as the programmer. example.py has everythign you need to get started bug a brief summary is below:

**GeSrtp** -
This Class contains the main libary code for reading / writing from the PLC.

**GeSrtpResponse** -
This Class is a structure to hold the response from the PLC, currently we are only interested in the register data, but the PLC does return other information, that could be added here for debugging etc. There are 2 status registers included today, although there usefulness is questionable.

**GE_SRTP_Messages** -
This Module contains multiple default message headers in byte array format.
Typically to talk to the PLC, start with one of these and modify the bytes as needed.


    from lib.GE_SRTP import GeSrtp

    #Example to read a single Word register from GE PLC:
    plc = GeSrtp(args.plc_ip) 
    plc.initConnection()
    result = plc.readSysMemory(args.reg)
    print("The Result from PLC = {}".format(result.register_result))
    plc.closeConnection()

