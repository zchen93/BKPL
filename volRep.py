"""
Author:
Fred Chen
Hardware Engineer
Communication Hardware Delivery
Global Devices
Landis+Gyr Technology Inc.
Alpharetta, Georgia, USA
JAN 2020
Contact: fred.chen@landisgyr.com
"""

import _commandLib
import _initPort
import datetime
import threading
import time
#import numpy as np# pip install numpy
import csv
import sys

TimeStamp = time.strftime('%Y%m%d_%H%M%S')

"""
Redirecting console output as log files
"""
RunConOutDir = str("./conout")
RunConOutFileName = str("RunConOut_" + TimeStamp + ".log")
RunConOutFile = str(RunConOutDir + '/' + RunConOutFileName)
OpenFile_RunConOut = open(RunConOutFile, 'w')
#sys.stdout = open(RunConOutDir + '/' + RunConOutFileName,'w')

"""
Directing result file written directory
"""
ResOutDir = str("./res")
ResOutFileName = str("ResOut_" + TimeStamp + ".txt")

EstablishedPort = _initPort.portsAvailableonComputer()
_commandLib.connMgr(EstablishedPort, "destruct")
_commandLib.enRemote(_commandLib.connMgr(EstablishedPort, "open"))

Result_V = []
Result_T = []
Count = 0
#enableTransOperation = _commandLib.ccTransCurrent(_commandLib.connMgr(EstablishedPort, "open"))
#print(enableTransOperation)

"""
CSV Writer:
"""
csvfile = open(ResOutDir + '/' + ResOutFileName, 'w', newline='')
writer = csv.writer(csvfile, delimiter=';', quotechar="'") # I don't fully understand why do we define writer this way...
# https://stackoverflow.com/questions/44073900/csv-writer-removes-quotes-and-adds-newline
# https://pymotw.com/2/csv/
writer.writerow(['SEP=,'])
writer.writerow(['Date & Time, Voltage[V]'])

"""
Methods that do the work:
"""
def periodReadV(Interval):
#def periodReadV(Interval, Threshold):
    # Interval Unit: seconds
    global Count
    try:
        NextCall = time.time()
        _commandLib.loadOn(_commandLib.connMgr(EstablishedPort, "open"))
        while float(_commandLib.readV(_commandLib.connMgr(EstablishedPort, "open"))) > 8.2:
        #while Count < 5:
            VolRead = _commandLib.readV(_commandLib.connMgr(EstablishedPort, "open"))
            Result_V.append(VolRead)
            Result_T.append(time.strftime("%m/%d/%Y %H:%M:%S")) # Formatting time to make Excel calculating the time difference better.
            # NextCall += Interval
            line = (time.strftime("%m/%d/%Y %H:%M:%S") + ',' + VolRead + ',,,,,,,')
            NextCall += Interval # Seconds
            Count += 1
            writer.writerow({line})

            MSG_ConOut = str("Iteration: " + str(Count) + " | Timestamp: " + time.strftime("%m/%d/%Y %H:%M:%S") + " | Voltage: " + VolRead)
            print(MSG_ConOut)
            OpenFile_RunConOut.write(MSG_ConOut + "\n")

            time.sleep(NextCall - time.time())

            if float(_commandLib.readV(_commandLib.connMgr(EstablishedPort, "open"))) <= 8.2:
                break
        MSG_Volow = str("Voltage Reached/Below Threshold.")

        print(MSG_Volow)
        OpenFile_RunConOut.write(MSG_Volow + "\n")

        _commandLib.loadOff(_commandLib.connMgr(EstablishedPort, "open"))

    except KeyboardInterrupt:
        MSG_KBItr = str("Interrupted by user pressing 'CTRL+C'.")
        print(MSG_KBItr)
        OpenFile_RunConOut.write(MSG_KBItr + "\n")
        _commandLib.loadOff(_commandLib.connMgr(EstablishedPort, "open"))

#Thread_1 = threading.Thread(target=periodReadV(VoltageQueryInterval))
#Thread_1.start()
def outro():
    if len(Result_V) > 0:
        MSG_Completion = str("Result writing complete. Readings: " + str(len(Result_V)))
        print(MSG_Completion)
        OpenFile_RunConOut.write(MSG_Completion + "\n")
    else:
        MSG_EptyRes = str("Empty result detected.")
        print(MSG_EptyRes)
        OpenFile_RunConOut.write(MSG_EptyRes + "\n")

    csvfile.close()
    _commandLib.loadOff(_commandLib.connMgr(EstablishedPort, "open"))

periodReadV(3)
outro()
