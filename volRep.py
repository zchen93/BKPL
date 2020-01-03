"""
Author:
Fred Chen
Hardware Delivery Team
Landis+Gyr Technology Inc.
Alpharetta, Georgia, USA
DEC 2019
Contact: fred.chen@landisgyr.com
"""

import _commandLib
import _initPort
import datetime
import threading
import time
import numpy as np# pip install numpy
import csv
import sys

TimeStamp = time.strftime('%Y%m%d_%H%M%S')

"""
Redirecting console output as log files
"""
RunConOutDir = str("./conout")
RunConOutFileName = str("RunConOut_" + TimeStamp + ".log")
sys.stdout = open(RunConOutDir+ '/' + RunConOutFileName,'w')

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

def periodReadV(Interval):
#def periodReadV(Interval, Threshold):
    # Interval Unit: seconds
    global Count
    try:
        NextCall = time.time()
        _commandLib.loadOn(_commandLib.connMgr(EstablishedPort, "open"))
        while float(_commandLib.readV(_commandLib.connMgr(EstablishedPort, "open"))) > 7.80:
        #while Count < 5:
            VolRead = _commandLib.readV(_commandLib.connMgr(EstablishedPort, "open"))
            Result_V.append(VolRead)
            Result_T.append(time.strftime("%m/%d/%Y %H:%M:%S")) # Formatting time to make Excel calculating the time difference better.
            # NextCall += Interval
            NextCall += Interval # Seconds
            time.sleep(NextCall - time.time())
            Count += 1
            print("Iteration: " + str(Count) + " | Timestamp: " + time.strftime("%m/%d/%Y %H:%M:%S") + " | Voltage: " + VolRead)

            if float(_commandLib.readV(_commandLib.connMgr(EstablishedPort, "open"))) <= 7.80:
                break

        print("Voltage Reached/Below Threshold.")
        _commandLib.loadOff(_commandLib.connMgr(EstablishedPort, "open"))

    except KeyboardInterrupt:
        print("Interrupted by user pressing 'CTRL+C'.")
        _commandLib.loadOff(_commandLib.connMgr(EstablishedPort, "open"))

#Thread_1 = threading.Thread(target=periodReadV(VoltageQueryInterval))
#Thread_1.start()

periodReadV(120)

"""
CSV Writer:
"""
csvfile = open(ResOutDir + '/' + ResOutFileName, 'w', newline='')
try:
    writer = csv.writer(csvfile, delimiter=';', quotechar="'") # I don't fully understand why do we define writer this way...
    # https://stackoverflow.com/questions/44073900/csv-writer-removes-quotes-and-adds-newline
    # https://pymotw.com/2/csv/
    writer.writerow(['SEP=,'])
    writer.writerow(['Date & Time, Voltage[V]'])

    if len(Result_V) > 0:
        for i in range(len(Result_V)):
            line = (Result_T[i] + ',' + Result_V[i] + ',,,,,,,')
            #print(line)
            writer.writerow({line})
        print("Result writing complete.")
    else:
        print("Empty result detected. ")
    _commandLib.loadOff(_commandLib.connMgr(EstablishedPort, "open"))
finally:
    csvfile.close()
    _commandLib.loadOff(_commandLib.connMgr(EstablishedPort, "open"))
