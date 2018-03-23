import serial

class DeviceError(Exception):
    pass

class NoChannelWarning(Warning):
    pass

class Tripped(Warning):
    pass

class HAMEGChannel(object):
    def __init__(self, supply, chNumber, vSet=1.0, iSet=0.1, turnOnNow=False):
        self._supply = supply
        self._chNumber = chNumber
        self.SetVoltage(vSet)
        self.SetCurrent(iSet)
    def SendMessage(self, msg):
        self._raising()
        self._supply.SendMessage(msg)
    def GetSupply(self):
        return self._supply
    def getNumber(self):
        return self._chNumber
    def _raising(self):
        self._supply.SendMessage("INST OUT%d\n"%(self._chNumber))
    def SetVoltage(self, vSet=1):
        self.SendMessage("SOUR:VOLT %.8f\n"%(vSet))
    def SetCurrent(self, iSet=0.1):
        self.SendMessage("SOUR:CURR %.8f\n"%(iSet))
    def SetVoltageCurrent(self, vSet=1, iSet=0.1):
        self.SendMessage("SOUR:VOLT %.8f\nSOUR:CURR %.8f\n"%(vSet,iSet))
    def OnOff(self, state):
        if state:
            self.TurnOn()
        else:
            self.TurnOff()
    def TurnOn(self):
        self.SendMessage("OUTP ON\n")
    def TurnOff(self):
        self.SendMessage("OUTP OFF\n")
    def MeasureVoltage(self):
        self.SendMessage("MEAS:VOLT?\n")
        return float(self._supply.readMessage())
    def MeasureCurrent(self):
        self.SendMessage("MEAS:CURR?\n")
        return float(self._supply.readMessage())
    def isTripped(self):
        self.SendMessage("FUSE:TRIP?\n")
        if int(self._supply.readMessage())!=0:
            return True
        else:
            return False

class HAMEGSupply():
    def __init__(self, numberOfPort=3, portname="/dev/ttyUSB0", devicename="HAMEG"):
        self.__portname = portname
        self._hameg = serial.Serial(self.__portname, 9600, rtscts=True)
        self._hameg.write("*IDN?\n")
        if not ("HAMEG") in self._hameg.readline():
            raise DeviceError("That is not HAMEG")
        self._ports = list()
        for ch in range(1, numberOfPort+1):
            self._ports.append(HAMEGChannel(self,ch))
    def SetAllVoltageCurrent(self,vSet=1.0,iSet=0.1):
        for port in self._ports:
            port.SetVoltageCurrent(vSet, iSet)
    def GetPort(self, portNumber, startOne=True): 
        if startOne:
            index = portNumber-1
        else:
            index = portNumber
        try:
            return self._ports[index]
        except IndexError:
            raise NoChannelWarning("There is no port No.%d"%(index))
    def SendMessage(self, msg):
        self._hameg.write(msg)
    def ReadMessage(self):
        return self._hameg.readline()
    def _simpleQuary(self, func):
        for port in self._ports:
            func(port)
    def OnAll(self):
        self._simpleQuary(HAMEGChannel.TurnOn)
    def OffAll(self):
        self._simpleQuary(HAMEGChannel.TurnOff)
    def OnOutput(self):
        self.SendMessage("OUTP:GEN ON\n")
    def OffOutput(self):
        self.SendMessage("OUTP:GEN OFF\n")
    def CheckTripped(self):
        result = list()
        for port in self._ports:
            if HAMEGChannel.isTripped(port):
                result.append(port.getNumber())
        return result

if __name__ == "__main__":
    print("HAMEG Serial Messenger")
    hameg = HAMEGSupply()
    while True:
        try:
            a = input("Message")
            hameg.SendMessage(a+"\n")
        except KeyboardInterrupt:
            print("Turn Off Messenger")
            exit()

