"""
This script will query the available ports on the computer that this script
is running on, and choose the right one for "B&K Precision 85xx Load".

Inspired by: https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
Customized by:
    Fred (Zengweijie) Chen
    Hardware Engineer
    Global Devices Delivery
    Landis+Gyr
    Alpharetta, GA 30022
    United States of America

*** SUPPORTS WINDOWS ONLY ***
"""

import sys
import glob
import serial.tools.list_ports
import serial
import re

def portsAvailableonComputer():
    ChosenPort = []
    ####################
    PortsConnected = serial.tools.list_ports.grep("Prolific") # Quick and dirty "grep" technique. A B&K IT-E132B USB-TTL adapter is used, which will show up as "Prolific USB-to-Serial Comm Port"
    for port, desc, hwid in sorted(PortsConnected):
        #ChosenPort = str("{}: {} [{}]".format(port, desc, hwid))
        ChosenPort = str("{}".format(port))
    #print("Your B&K Load is connected on port: " + ChosenPort)
    return ChosenPort
####################################################
# Port = portsAvailableonComputer()

if __name__ == '__main__':
    """
    If calling this script directly, print below message:
    """
    print("Your B&K Load is connected on port: " + portsAvailableonComputer())
