"""

Author: Fred Chen
Dec 2019

This file is the 'library' for the proper hexadecimal commands send to the B&K -
85xx Load, in the format of python methods.

Worth reading:
https://stackoverflow.com/questions/16926130/convert-to-binary-and-keep-leading-zeros-in-python
https://docs.python.org/2/library/string.html#format-specification-mini-language
"""

import _initPort
import serial
import encodings

EstablishedPort = _initPort.portsAvailableonComputer()
#print(EstablishedPort)

#############################
def connMgr(PortInput, Action): # "estConn"
    ConnInstance = serial.Serial()
    ConnInstance.baudrate = 38400 # In provided example, Baud was 9600, which was wrong.
    ConnInstance.port = PortInput
    if Action == "open":
        ConnInstance.open()
        return ConnInstance
    elif Action == "close":
        ConnInstance.close()
    elif Action == "destruct":
        ConnInstance.__del__() # close when port is free'd
    # print(ConnInstance.is_open)

# **** the 3 functions below were inspired by the sourcecodes provided by B&K
def serialComm(Command, Session, ifRead): # "cmd8500"
    #print("Command: ", hex(Command[2]))
    #print("From serialComm method. \nCommand being sent:" + decToHex(Command))
    Session.write(Command)
    strrrr = [00]*26
    RespReturned = [0]*26
    if ifRead == True:
        Resp = Session.read(26)
        assert(len(Resp) == 26)
        #print(Resp)
        RespinList = list(Resp)
        ###################
        for i in RespinList:
            RespReturned[RespinList.index(i)] = format(i,'02X') # use "format" to convert for 2-digit HEX
        ###################
        #print("RespinList: ")
        #print(RespReturned)

    return RespReturned

def decToHex(dec): # "PrintBuff"
    # Used to parse the returned message
    r = ""
    for s in range(len(dec)):
        #r += ","
        #r += str(s)
        #r += ": "
        r += hex(dec[s]).replace('0x','')
    return r

def getReading(InputStr, StartPos, BytesLength):
    """
    Takes in the received hex String,
    parse the proper reading by giving the starting position and # of bytes
    Returns calculated reading from the equipment
    """
    pr = "" # PreliminaryResult
    for i in range(1, BytesLength + 1) :
        pr += str(InputStr[StartPos + BytesLength - i]) # Concactenate different bytes into 1 string.
        # Convert Hex String into Hex, and eventually Dec
        """
        For example, we want to interpret the returned string from byte 4 (position 3) till byte 7 (position 6);
        since the Little-Endian format would require us to read from right to left bytewise, and left to right within the byte,
        the string that makes sense would be concactenating from position 6 -> position 5 -> position 4 -> position 3.
        Here, StartPos + BytesLength = 7, and the index of the input list would reduce by 1 in every iteration of this "for" loop.
        Contact Fred Chen if you need more details (fred.chen@landisgyr.com)
        """
    prr = int(pr.encode(), 16) # Hex String -> Hex Byte -> Integer
    ar = '{:.10}'.format(float(prr/1000)) # Wanted it to display all digits after '.'
    #print("PR = " + str(ar))
    return ar

def cmdSum(r):
    sum = 0
    for i in range(len(r)):
        sum += r[i]
    return 0xFF & sum
# the 3 functions above were inspired by the sourcecodes provided by B&K

"""
array[2] is usually the function of BK8500 Load
"""

def enRemote(s):
    #enable remote mode
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x20
    RawCmd[3] = 1
    RawCmd[25] = cmdSum(RawCmd)
    #return RawCmd
    print(RawCmd)
    serialComm(RawCmd, s, True)
    return RawCmd

def readV(s):
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x5F
    RawCmd[3] = 1
    RawCmd[25] = cmdSum(RawCmd)
    #return RawCmd
    #print("Attempting to read current voltage")
    #print(RawCmd)
    StrReturned = serialComm(RawCmd, s, True)
    VoltageReading = getReading(StrReturned, 3, 4) # (result, StartPos, BytesLength)
    #print("String Returned: " + StrReturned)
    #print("Voltage = " + str(VoltageReading))
    return VoltageReading

def loadOff(s):
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x21
    RawCmd[3] = 0
    RawCmd[25] = cmdSum(RawCmd)
    StrReturned = serialComm(RawCmd, s, True)
    return StrReturned

def loadOn(s):
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x21
    RawCmd[3] = 1
    RawCmd[25] = cmdSum(RawCmd)
    StrReturned = serialComm(RawCmd, s, True)
    return StrReturned

#def ccTransCurrent(s, IaLvl, IaTau, IbLvl, IbTau, TransMode, MethodMode):
def ccTransCurrent(s):
    """
    Currently, the current pattern has been set to:
        Section A: 64ms | 60mA
        Section B: 936ms | 378mA
        Continuous Mode
    """
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x32
    RawCmd[3] = 0x3C
    RawCmd[7] = 0x80
    RawCmd[8] = 0x02
    RawCmd[9] = 0xC4
    RawCmd[10] = 0x0E
    RawCmd[13] = 0x90
    RawCmd[14] = 0x24
    RawCmd[15] = 0x0
    RawCmd[25] = cmdSum(RawCmd)
    StrReturned = serialComm(RawCmd, s, True)
    return StrReturned

def setListOp(s):
    #Setup list operation
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x3A
    RawCmd[3] = 1
    RawCmd[25] = cmdSum(RawCmd)

    serialComm(RawCmd, s, "")
    return RawCmd

def readListOp(s):
    #read list operation
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x3B
    RawCmd[3] = 1
    RawCmd[25] = cmdSum(RawCmd)

    serialComm(RawCmd, s, True)
    return RawCmd

def setListRpt(s):
    #set list repeat
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x3c
    RawCmd[3] = 1

    RawCmd[25] = cmdSum(RawCmd)

    serialComm(RawCmd, s, "")
    return RawCmd

def readListRpt(s):
    #read list repeat
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x3d
    RawCmd[3] = 1
    RawCmd[25] = cmdSum(RawCmd)

    serialComm(RawCmd, s, True)
    return RawCmd

def setStep(s):
    #set the number of steps
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x3e
    RawCmd[3] = 4
    RawCmd[4] = 1
    RawCmd[25] = cmdSum(RawCmd)

    serialComm(RawCmd, s, "")
    return RawCmd

def readStep(s):
    #read the number of steps
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x3f
    RawCmd[3] = 1
    RawCmd[25] = cmdSum(RawCmd)
    serialComm(RawCmd, s, True)
    return RawCmd

def setStep(s):
    #set a step!
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x40
    RawCmd[3] = 1
    RawCmd[5] = 0xAA
    RawCmd[9] = 0xff
    RawCmd[25] = cmdSum(RawCmd)

    serialComm(RawCmd, s, "")
    return RawCmd

def readCurrStep(s):
    #read that step
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x41
    RawCmd[3] = 1
    RawCmd[25] = cmdSum(RawCmd)

    serialComm(RawCmd, s, "")
    return RawCmd

def setName(s):
    ###############
    #Set the name
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x48
    RawCmd[3] = 82
    RawCmd[4] = 121
    RawCmd[25] = cmdSum(RawCmd)

    serialComm(RawCmd, s, "")
    return RawCmd

def readName(s):
    #read that name
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x49
    RawCmd[3] = 1
    RawCmd[25] = cmdSum(RawCmd)

    serialComm(RawCmd, s, "")
    return RawCmd

def saveList(s):
    #save the list
    RawCmd = [0]*26
    RawCmd[0] = 0xAA
    RawCmd[2] = 0x4C
    RawCmd[3] = 2
    RawCmd[25] = cmdSum(RawCmd)

    serialComm(RawCmd, s, "")
    return RawCmd

if __name__ == '__main__':
    connMgr(EstablishedPort, "destruct")
    #enRemote(connMgr(EstablishedPort, "open"))
    readV(connMgr(EstablishedPort, "open"))
    #readStep(connMgr(EstablishedPort, "open"))
