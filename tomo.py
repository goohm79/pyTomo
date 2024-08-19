# This is a TOMO1S12V2I class Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import serial
import serial.tools.list_ports


class TOMO1S12V2I:
  def __init__(self, comPort="/dev/ttyACM0"):

    self.Meas = {}
    self.ZoneActive = {}
    self.IsourceChannel= 0
    self.Led=0
    self.suEN = 0
    self.ZoneActive["A1"]=0
    self.ZoneActive["A2"]=0
    self.SeqU = {}
    self.SeqU ["I01"] = 50 # uA
    self.SeqU ["I02"] = 100 # uA
    self.SeqU ["TuA"] = 10 # s
    self.SeqU ["TuB"] = 120 # s
    self.SeqU ["TuC"] = 30 # s
    self.SeqU ["TuD"] = 120 # s
    self.SeqU ["TuE"] = 10 # s
    self.SeqU ["MeasPerDay"] = 2 # sample per day
    self.SeqU ["SourcePerWeek"] = 1 # source per week
    self.SeqU ["TempoMs"] = 1 # tempo ms
    self.SeqU ["Conf"] = 1 # confA
    self.comPort = comPort
    try:
        self.com = serial.Serial(port=self.comPort, baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
        self.com.flushInput()
        self.com.flushOutput()
    except:
        print("comPort: " + self.comPort + " could not connected to TOMO1S12V2I")

  def listCom(self, data=None):
    return list(serial.tools.list_ports.comports())
    
  def flushCom(self, data=None):
    self.com.flushInput()
    self.com.flushOutput()

  def wCom(self, data=None):
    n = 0
    self.com.flushInput()
    self.com.flushOutput()
    a = data.encode('utf-8')
    while n == 0:
        self.com.write(data=a)
        ret = self.com.readlines()
        for line in ret:
            if line.decode() == 'OK\r\n' or line.decode() == 'AT_RECONF_ERROR\r\n':
                n=1
  def wrCom(self, data=None):
    n = 0
    self.com.flushInput()
    self.com.flushOutput()
    a = data.encode('utf-8')
    self.com.write(data=a)
    r = self.com.readline()
    val = r.decode()
    ret = val.split('=', 1)
    return ret[1]

  def wrMeasCom(self, data=None):
    n = 0
    self.com.flushInput()
    self.com.flushOutput()
    a = data.encode('utf-8')
    self.com.write(data=a)
    r = self.com.readlines()
    return r[0]


  def rCom(self):
    ret = self.com.readlines()
    if ret.decode() == 'OK\r\n':
      return 999999999
    else:
      return int(ret.decode(), 16)

  def setLed(self,red=0, green=0):
    strVal = "AT+LED=" + str(green) + str(red) +"\r\n"
    self.wCom(data=strVal)

  def getLed(self):
    strVal = "AT+LED=?\r\n"
    self.wCom(data=strVal)
    ret = self.rCom()
    if ret != 999999999:
        self.Led = ret
        return self.Led 
    
  def setPwr(self,pwrIV=0, pwrS=0, pwrS33V=0, pwrCel=0):
    strVal = "AT+PWR=" + str(pwrIV) + str(pwrS) + str(pwrS33V) +  str(pwrCel) +"\r\n"
    self.wCom(data=strVal)

  def getPwr(self):
      strVal = "AT+PWR=?\r\n"
      self.wCom(data=strVal)
      ret = self.rCom()
      if ret != 999999999:
         self.Pwr = ret
         return self.Pwr 

  def setIsource(self, IuA=0):
    strVal = "AT+IVAL=" + str(IuA)+"\r\n"
    self.wCom(data=strVal)
    
  def getIsource(self):
    strVal = "AT+IVAL=?\r\n"
    ret = self.wrCom(data=strVal)
    if ret != 999999999:
         self.Isource = int(ret)
         return self.Isource
    
  def su_setMainTask(self, En=0):
    strVal = "AT+EN=" + str(En)+"\r\n"
    self.wCom(data=strVal)
    
  def su_getMainTask(self):
    strVal = "AT+EN=?\r\n"
    ret = self.wrCom(data=strVal)
    if ret != 999999999:
         self.suEN = int(ret)
         return self.suEN 
     
  def setIon(self, En=0):
    strVal = "AT+ION=" + str(En)+"\r\n"
    self.wCom(data=strVal)
    
  def getIon(self):
    strVal = "AT+ION=?\r\n"
    ret = self.wrCom(data=strVal)
    if ret!= 999999999:
         self.Ion = int(ret)
         return self.Ion   
    
  def setIpol(self, Pol=0):
    strVal = "AT+IPOL=" + str(Pol)+"\r\n"
    self.wCom(data=strVal)
    
  def getIpol(self):
    strVal = "AT+IPOL=?\r\n"
    ret = self.wrCom(data=strVal)
    if ret != 999999999:
         self.Ipol = int(ret)
         return self.Ipol 
    
  def setActiveZone(self, A1=0, A2=0):
    self.ZoneActive["A1"]=A1
    self.ZoneActive["A2"]=A2
    strVal = "AT+AZ=" + str(self.ZoneActive["A1"]) + str(self.ZoneActive["A2"]) +"\r\n"
    self.wCom(data=strVal)

  def getActiveZone(self, A1=0, A2=0):
    strVal = "AT+AZ=?\r\n"
    ret = self.wrCom(data=strVal)
    if ret != 999999999:
         val = int(ret)
         if val == 0 :
             self.ZoneActive["A1"]=0
             self.ZoneActive["A2"]=0
         elif val ==1:
             self.ZoneActive["A1"]=1
             self.ZoneActive["A2"]=0
         elif val == 2:
             self.ZoneActive["A1"]=0
             self.ZoneActive["A2"]=1
         elif val == 3:
             self.ZoneActive["A1"]=1
             self.ZoneActive["A2"]=1

  def setIchannel(self, channel ="0"):
    self.IsourceChannel = int(channel)
    conf = '000000000000'
    if self.IsourceChannel == 0:
        conf = '000000000000'
    if self.IsourceChannel == 1:
        conf = '100000000000'
    if self.IsourceChannel == 2:
        conf = '010000000000'  
    if self.IsourceChannel == 3:
        conf = '001000000000'
    if self.IsourceChannel == 4:
        conf = '000100000000'
    if self.IsourceChannel == 5:
        conf = '000010000000'
    if self.IsourceChannel == 6:
        conf = '000001000000'
    if self.IsourceChannel == 7:
        conf = '000000100000'
    if self.IsourceChannel == 8:
        conf = '000000010000'
    if self.IsourceChannel == 9:
        conf = '000000001000'
    if self.IsourceChannel == 10:
        conf = '000000000100'
    if self.IsourceChannel == 11:
        conf = '000000000010'
    if self.IsourceChannel == 12:
        conf = '000000000001'
    if self.IsourceChannel == 'ALL':
        conf = '111111111111'
    strVal = "AT+SCH=" + conf +"\r\n"
    self.wCom(data=strVal)

  def getIchannel(self):
    strVal = "AT+SCH=?\r\n"
    r = self.wrCom(data=strVal)
    val = r[0].split('=', 1)
    ret = val[0]
    if ret != 999999999:
        if ret =='000000000000':
             self.IsourceChannel = 0
        if ret =='100000000000':
             self.IsourceChannel = 1     
        if ret =='010000000000':
             self.IsourceChannel = 2
        if ret =='001000000000':
             self.IsourceChannel = 3
        if ret =='000100000000':
             self.IsourceChannel = 4
        if ret =='000010000000':
             self.IsourceChannel = 5
        if ret =='000001000000':
             self.IsourceChannel = 6
        if ret =='000000100000':
             self.IsourceChannel = 7
        if ret =='000000010000':
             self.IsourceChannel = 8
        if ret =='000000001000':
             self.IsourceChannel = 9
        if ret =='000000000100':
             self.IsourceChannel = 10
        if ret =='000000000010':
             self.IsourceChannel = 11
        if ret =='000000000001':
             self.IsourceChannel = 12  
        if ret =='111111111111':
             self.IsourceChannel = 'ALL'   
        return self.IsourceChannel
         
  def setAcquire(self):
     strVal = "AT+MEAS=?\r\n"
     ret = self.wrMeasCom(data=strVal)
     if ret != 999999999:
         val = ret.decode()
         tabStrVal = val.split(';', 21)    
         idx = 5     
         self.Meas["ISOURCE"]=float(tabStrVal[idx+1])
         self.Meas["VSOURCE"]=float(tabStrVal[idx+2])
         self.Meas["V1"]=float(tabStrVal[idx+3])
         self.Meas["V2"]=float(tabStrVal[idx+4])
         self.Meas["V3"]=float(tabStrVal[idx+5])
         self.Meas["V4"]=float(tabStrVal[idx+6])
         self.Meas["V5"]=float(tabStrVal[idx+7])
         self.Meas["V6"]=float(tabStrVal[idx+8])
         self.Meas["V7"]=float(tabStrVal[idx+9])
         self.Meas["V8"]=float(tabStrVal[idx+10])
         self.Meas["V9"]=float(tabStrVal[idx+11])
         self.Meas["V10"]=float(tabStrVal[idx+12])
         self.Meas["V11"]=float(tabStrVal[idx+13])
         self.Meas["V12"]=float(tabStrVal[idx+14]) 
         self.Meas["I1"]=float(tabStrVal[idx+15])
         self.Meas["I2"]=float(tabStrVal[idx+16])
          
         
  def getMeas(self, channel=''):
       try:
           return self.Meas[channel]
       except:
           return None
       
  def setSeqU(self, I01=50, I02=100, TuA=10, TuB=120, TuC=30, TuD=120, TuE=10, msTempo=15, MeasPerDay=2,SourcePerWeek=1,Conf=1):
      self.SeqU ["I01"] = I01 # uA
      self.SeqU ["I02"] = I02 # uA
      self.SeqU ["TuA"] = TuA # s
      self.SeqU ["TuB"] = TuB # s
      self.SeqU ["TuC"] = TuC # s
      self.SeqU ["TuD"] = TuD # s
      self.SeqU ["TuE"] = TuE # s
      self.SeqU ["MeasPerDay"] = MeasPerDay # sample per day
      self.SeqU ["SourcePerWeek"] = SourcePerWeek # source per week
      self.SeqU ["TempoMs"] = msTempo # k
      self.SeqU ["Conf"] = Conf # configuritaon number
      strVal = "AT+SU="
      strVal +=  str(self.SeqU ["I01"]) + ","
      strVal +=  str(self.SeqU ["I02"]) + ","  
      strVal +=  str(self.SeqU ["TuA"]) + ","  
      strVal +=  str(self.SeqU ["TuB"]) + ","
      strVal +=  str(self.SeqU ["TuC"]) + ","  
      strVal +=  str(self.SeqU ["TuD"]) + ","  
      strVal +=  str(self.SeqU ["TuE"]) + ","  
      strVal +=  str(self.SeqU ["MeasPerDay"]) + ","  
      strVal +=  str(self.SeqU ["SourcePerWeek"]) + ","  
      strVal +=  str(self.SeqU ["TempoMs"]) + ","  
      strVal +=  str(self.SeqU ["Conf"]) +"\r\n"
      self.wCom(data=strVal)
      
  def getSeqU(self):
      strVal = "AT+SU=?,1\r\n"
      ret = self.wrCom(data=strVal)
      if ret != 999999999:
         tabStrVal = ret.split(',', 9)    
         self.SeqU ["I01"] = int(tabStrVal[0]) # uA
         self.SeqU ["I02"] = int(tabStrVal[1]) # uA
         self.SeqU ["TuA"] = int(tabStrVal[2]) # s
         self.SeqU ["TuB"] = int(tabStrVal[3]) # s
         self.SeqU ["TuC"] = int(tabStrVal[4]) # s
         self.SeqU ["TuD"] = int(tabStrVal[5]) # s
         self.SeqU ["TuE"] = int(tabStrVal[6]) # s
         self.SeqU ["MeasPerDay"] = int(tabStrVal[7]) # sample per day
         self.SeqU ["SourcePerWeek"] = int(tabStrVal[8]) # source per week
         self.SeqU ["TempoMs"] = int(tabStrVal[9]) # source per week
         
          

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dut = TOMO1S12V2I(comPort="/dev/ttyACM0")