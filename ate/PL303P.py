
import serial
from time import sleep

class PL303:
    def __init__(self, comPort = "/dev/PL303_COM"):
        self.test = 1
        print('Class PL303')
        self.OutputState = 0
        self.comPort = comPort
        self.SetCom()
    
    def SetCom(self):   
        try:
            self.com = serial.Serial(port=self.comPort, baudrate=9600, bytesize=8, timeout=2,
                                     stopbits=serial.STOPBITS_ONE)
            ret = self.Read("*IDN?")
            print("PowerSupply PL303-P Id: " + str(ret))
            return 1
            
        except:
            print("comPort: " + self.comPort + " could not connected to PowerSupply PL303-P")     
            return 1
    # Press the green button in the gutter to run the script.
    def Output(self, val=None):
        if val == None:
            return self.OutputState
        elif val == 1 or val == 'ON' or val == 'on' or val == 'On':
            if self.Write('OP1 1') == 1:
                self.OutputState = 1
        elif val == 0 or val == 'OFF' or val == 'off' or val == 'Off':
            if self.Write('OP1 0') == 1:
                self.OutputState = 0
        

    def Set(self, fct=None, val=None):
            if fct == 'V' or fct == 'v':
                if val == None:
                    ret = self.Get('V1?')
                    return float(ret)
                else:
                    self.Write('V1 ' + str(val))
            elif fct == 'A' or fct == 'a' or fct == 'I' or fct == 'i':
                if val == None:
                    ret = self.Get('I1?')
                    return float(ret)
                else:
                    if val > 2: #protection courant max admissible par le relai
                        val = 2
                    self.Write('I1 ' + str(val))

    def Get(self, val=None):
        ret = str(self.Read(val))
        characters = "bVA'\\r\\n"  # supprime les caracters listés
        ret = ''.join(x for x in ret if x not in characters)
        ans = ret.split(' ')
        return ans[(len(ans)-1)]

    def Meas(self, fct=None):
        if fct == 'V' or fct == 'v':
            ret = self.Get('V1O?')
            if self.test == 0: 
                return float(ret)
            else:
                sleep(0.1)
                return 99.9
        elif fct == 'A' or fct == 'a' or fct == 'I' or fct == 'i':
            ret = self.Get('I1O?')
            if self.test == 0: 
                return float(ret)
            else:
                sleep(0.1)
                return 'A'

    def Write(self, val=None):
        try:
            self.com.flushInput()
            self.com.flushOutput()
            val = val + '\n\r'
            val = val.encode('utf-8')
            self.com.write(data=val)
            return 1
        except:
            return 0

    def Read(self, cmd=None):
        try:
            self.com.flushInput()
            self.com.flushOutput()
            if self.Write(cmd) == 1:
                return self.com.readline()
            else:
                return -1
        except:
            return -1

if __name__ == '__main__':
    dut = PL303()
    dut.Set('V', 10.0)
    dut.Set('I', 1.0)
    dut.Output(0)
    sleep(2)
    while 1:
        print(str(dut.Meas('V')))
        print(str(dut.Meas('I')))
    dut.Output(1)
    sleep(2)
    print(str(dut.Meas('V')))
    print(str(dut.Meas('I')))

