import sys
import time
import os.path
import threading
import datetime

from ate.tomo import TOMO1S12V2I
from ate.PL303P import PL303
from gui.toolsGui import DIGIT, PMLINE, Worker
from gui.p303Gui import PL303GUI

from pickle import NONE
from PySide6.QtCore import SIGNAL, QObject, QTimer
from PySide6 import  QtWidgets, QtGui # -*- coding: utf-8 -*-
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtGui import QColor

pal = QPalette()
pal.setColor(QPalette.Base, QColor(60, 60, 60))
pal.setColor(QPalette.Button, QColor(60, 60, 60))
pal.setColor(QPalette.Text, QColor(255, 255, 255))
pal.setColor(QPalette.WindowText, QColor(255, 255, 255))

palRed = QPalette()
palRed.setColor(QPalette.Base, QColor(60, 60, 60))
palRed.setColor(QPalette.Button, QColor(60, 60, 60))
palRed.setColor(QPalette.Text, QColor(255, 0, 0))
palRed.setColor(QPalette.WindowText, QColor(255, 0, 0))
       
class MYP2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('p2PiloteGUI.py')
         # Now use a palette to switch to dark colors:
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText,QtGui.QColor(0, 0, 0))
        app.setPalette(palette)      
        
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        
        self.createVoltMeterGroupBox()
        self.createCurrentMeterGroupBox()
        self.createControlGroupBox()
        self.createTerminalGroupBox()
        self.createP2PiloteGroupBox()
        
        
        self.powerSupply = PL303GUI()

        #self.tomowf = TOMOWATERFLOW(x=1000,y=600)
        pixmap =QtGui.QPixmap('logo.png')
        self.lbllogo = QtWidgets.QLabel() 
        self.lbllogo.setPixmap(pixmap)
        
        self.initState = 0  
        self.t1State = 0
        self.P2State = 0
        self.pause =0
        self.start = 0   
        self.x = 0 
        self.y = 0 
        self.ActiveWheel = []

        oneLayout= QtWidgets.QGridLayout()
        oneGroupBox = QtWidgets.QGroupBox("")
        oneGroupBox.setGeometry(0,0,30,30)
        palette = oneGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        oneGroupBox.setPalette(palette)
        oneLayout.addWidget(self.lbllogo,0,0)
        #oneLayout.addWidget(self.controlGroupBox,1,0)
        #oneLayout.addWidget(self.terminalGroupBox,2,0)
        oneLayout.addWidget(self.voltMeterGroupBox,0,2)
        oneLayout.addWidget(self.currentMeterGroupBox,1,2)
        oneLayout.addWidget(self.powerSupply,0,3,3,3)
        
        oneLayout.setRowStretch(0,0)
        oneLayout.setColumnStretch(1, 1)  
        oneGroupBox.setLayout(oneLayout)
        
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.addWidget(oneGroupBox,0, 1)
        self.mainLayout.addWidget(self.P2PiloteGroupBox,1, 1)
        
        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setColumnStretch(1, 1)
        self.centralWidget.setLayout(self.mainLayout)
        
        self.connect(self.btnEnSeqU, SIGNAL("clicked()"),self.setP2Prog)  
        self.connect(self.btnCal, SIGNAL("clicked()"),self.setCal)
        
        self.initDut()

        
    def __del__(self):
        self.stopThreadReadLine()
       
    
        
    def startThreadReadLine(self):  
        if self.initState == 1:
            try:
                self.logDateTime = datetime.datetime.now()
                self.logFileName = "log_stage-" + str(self.stage.getVal()) + "_zone-" + self.inputboxZone.text() + "_date-" + str(self.logDateTime)
                file  = QtWidgets.QFileDialog.getSaveFileName(None, "Save a file csv", self.logFileName + ".csv",             "*.csv")
                self.logFileName = file[0]
                #self.view.initImage(self.logFileName + ".png")
  
                self.ExtractLogFileName = file[0]
                if not os.path.exists(self.ExtractLogFileName):
                    self.ExtractLogFile = open(self.ExtractLogFileName, "w")
                    self.strLine = "LEVEL;ZONE;DIRECTION;X;Y;MEAS\r"
                    self.ExtractLogFile.writelines(self.strLine)
                    self.ExtractLogFile.close()
                self.x = self.xcolumn.getVal()
                self.dut.startP2()
                # création de thread
                self.t1 = threading.Thread(target=self.printThreadReadLine)
                self.t1State=1
                self.t1.start()
                
                self.timer = QTimer()
                self.timer.setInterval(5000)
                self.timer.timeout.connect(self.timerImageViewrefresh)
                self.timer.start() 
            except:
                self.t1State=0
        
    def stopThreadReadLine(self):
        try: 
            self.timer.stop()
            try:
                self.ExtractLogFile.close()  
            except:
                None
            self.t1State=0
            self.t1.join()
            self.dut.stopP2()
        except:
            NONE
               
    def printThreadReadLine(self): 
        self.t1 = time.time()
        self.t2 = time.time()  
        while(self.t1State==1):
            if self.pause != 1 :  
                try:             
                    NONE
                except:
                    self.dut.flushCom() 
                    try:
                        self.ExtractLogFile.close() 
                    except:
                        NONE 
            else:
                self.dut.flushCom()  
                  
    def timerImageViewrefresh(self):
        try:
            NONE
        except:
            NONE
            
        
    def setP2Prog(self):
        if self.P2State  == 1:
            self.P2State = 0
            self.textEditTerminal.append("Stop P2 Program")
            self.textEditTerminal.append("Start TOMO Program")
            self.btnEnSeqU.setText("Enable P2 Prg.")
            self.dut.setP2toTomo()
        else:
            self.P2State = 1
            self.textEditTerminal.append("Stop TOMO Program")
            self.textEditTerminal.append("Start P2 Program")
            self.btnEnSeqU.setText("Enable Tomo Prg.")
            self.dut.setTomotoP2()
       
    def setCal(self):
        if self.t1State == 0:
            self.textEditTerminal.append("Set calibration")
            self.dut.setCal()
            self.displayMeas()
            
    def startSourceTaskThreadReadLine(self):  
        if self.initState == 1:
            try:
                # création de thread
                self.t1 = threading.Thread(target=self.printSourceTaskThreadReadLine)
                self.t1State=1
                self.t1.start()
                
            except:
                self.t1State=0
    
    def printSourceTaskThreadReadLine(self):   
        while(self.t1State==1):
            ExtStrLine = (str)(self.dut.rLineCom())
            self.ExtractLogFile = open(self.ExtractLogFileName, "a")
            self.ExtractLogFile.writelines(ExtStrLine)
            self.ExtractLogFile.close()
            try :
                print(ExtStrLine)
                tabStrVal = ExtStrLine.split(';', 22)
                end = tabStrVal[5]
                print(end)
                if end == 'H' :
                    self.t1State= 0   
            except:                             
                print(ExtStrLine)

    def initDut(self):   
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(60, 60, 60))
        pal.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))  
        pal.setColor(QPalette.Button, QColor(60, 60, 60))
        pal.setColor(QPalette.Text, QColor(255, 255, 255))
        if self.initState == 0 and self.t1State == 0:
            self.initState = 1
            try: 
                self.dut = TOMO1S12V2I(comPort="/dev/TOMO_COM")
                self.textEditTerminal.append("Connected to: " + "/dev/TOMO_COM")
                self.dut.stopP2Pilote()
                self.btnConnect.setText("Disconnect")
                pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
                self.btnConnect.setPalette(pal)            
                #self.dut.setPwr(pwrIV=1, pwrS=1, pwrS33V=1)
                self.textEditTerminal.append("Set power On")
                self.displayMeas()
                if self.dut.getP2() == 2:
                    self.btnEnSeqU.setText("Enable TOMO Prg.")
                    self.P2State  = 1
                else:
                    self.P2State  = 0
                    self.btnEnSeqU.setText("Enable P2 Pilote Prg.")
                
            except:
                self.initState = 0
                self.textEditTerminal.append("problem to connect to: " + "/dev/TOMO_COM")    
                   
           
    
    def getMainTaskState(self):
        if self.dut.su_getMainTask() ==1 : 
            self.btnEnSeqU.setText("SeqU STOP")
            self.t1State = 1
        else:
            self.t1State = 0
                  
            
    def displayMeas(self):
        if self.t1State == 0:
            self.textEditTerminal.append("Get measure")
            self.dut.setAcquireP2Pilote()
            self.vm1.lcd.display(self.dut.getMeas("V1"))
            self.vm2.lcd.display(self.dut.getMeas("V2"))
            self.vm3.lcd.display(self.dut.getMeas("V3"))
            self.vm4.lcd.display(self.dut.getMeas("V4"))
            self.vm5.lcd.display(self.dut.getMeas("V5"))
            self.vm6.lcd.display(self.dut.getMeas("V6"))
            self.am1.lcd.display(self.dut.getMeas("I1"))
            self.am2.lcd.display(self.dut.getMeas("I2"))
            self.am3.lcd.display(self.dut.getMeas("I3"))
            self.am4.lcd.display(self.dut.getMeas("I4"))
            self.am5.lcd.display(self.dut.getMeas("I5"))
            self.am6.lcd.display(self.dut.getMeas("I6"))
            
        
            
    
    def createTerminalGroupBox(self):
        
        self.terminalGroupBox = QtWidgets.QGroupBox("Terminal")
        self.terminalGroupBox.setGeometry(0,0,30,10)
        self.terminalGroupBox.setPalette(pal)
        mainLayout = QtWidgets.QGridLayout()  
       
        # cmd line
        self.textEditTerminal = QtWidgets.QTextEdit()  
        self.textEditTerminal.setText("")
        self.textEditTerminal.setPalette(pal)

        mainLayout.addWidget(self.textEditTerminal,0, 0,0,0)
        mainLayout.setRowStretch(1,1)
       
        self.terminalGroupBox.setLayout(mainLayout)
    
              
    def createControlGroupBox(self):
        self.controlGroupBox = QtWidgets.QGroupBox("Control")
        self.controlGroupBox.setGeometry(0,0,10,10)
        palette = self.controlGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.controlGroupBox.setPalette(palette)    
        mainLayout = QtWidgets.QGridLayout()  
      
       
        self.btnCal = QtWidgets.QPushButton("CALIBRATION")
        self.btnCal.setPalette(pal)
        self.btnCal.setDefault(True)
        mainLayout.addWidget(self.btnCal,1,1)
        

        lblTask = QtWidgets.QLabel()
        mainLayout.addWidget(lblTask,0, 0)
        lblTask.setText("Switch Tomo1S12V2I to P2")
        # Seq Unitai Measure
        self.btnEnSeqU = QtWidgets.QPushButton()
        self.btnEnSeqU.setText("Enable")
        self.btnEnSeqU.setPalette(pal)
        self.btnEnSeqU.setDefault(True)
        mainLayout.addWidget(self.btnEnSeqU,0, 1)
        
          
        
        mainLayout.setRowStretch(2,2)
        mainLayout.setColumnStretch(0, 1)
        self.controlGroupBox.setLayout(mainLayout)
    
   
        
       
    def createVoltMeterGroupBox(self):
        self.voltMeterGroupBox = QtWidgets.QGroupBox("VoltMeters  [mV]")
        self.voltMeterGroupBox.setGeometry(0,0,100,50)
        
        palette = self.voltMeterGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.voltMeterGroupBox.setPalette(palette)

        self.vm1 = DIGIT("V1")
        self.vm2 = DIGIT("V2")
        self.vm3 = DIGIT("V3")
        self.vm4 = DIGIT("V4")
        self.vm5 = DIGIT("V5")
        self.vm6 = DIGIT("V6")

        mainLayout = QtWidgets.QGridLayout()
        
        mainLayout.addWidget(self.vm1.GroupBox,0, 1)
        mainLayout.addWidget(self.vm2.GroupBox,0, 2)
        mainLayout.addWidget(self.vm3.GroupBox,0, 3)
        mainLayout.addWidget(self.vm4.GroupBox,0, 4)
        mainLayout.addWidget(self.vm5.GroupBox,0, 5)
        mainLayout.addWidget(self.vm6.GroupBox,0, 6)
        mainLayout.setRowStretch(0,0)
        self.voltMeterGroupBox.setLayout(mainLayout)
    
    
    def createCurrentMeterGroupBox(self):
        self.currentMeterGroupBox = QtWidgets.QGroupBox("AmpereMeters [mA]")
        self.currentMeterGroupBox.setGeometry(0,0,100,50)
        
        palette = self.currentMeterGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.currentMeterGroupBox.setPalette(palette)

        self.am1 = DIGIT("I1")
        self.am2 = DIGIT("I2")
        self.am3 = DIGIT("I3")
        self.am4 = DIGIT("I4")
        self.am5 = DIGIT("I5")
        self.am6 = DIGIT("I6")

        mainLayout = QtWidgets.QGridLayout()
        
        mainLayout.addWidget(self.am1.GroupBox,0, 1)
        mainLayout.addWidget(self.am2.GroupBox,0, 2)
        mainLayout.addWidget(self.am3.GroupBox,0, 3)
        mainLayout.addWidget(self.am4.GroupBox,0, 4)
        mainLayout.addWidget(self.am5.GroupBox,0, 5)
        mainLayout.addWidget(self.am6.GroupBox,0, 6)
        mainLayout.setRowStretch(0,0)
        self.currentMeterGroupBox.setLayout(mainLayout)        

    def createP2PiloteGroupBox(self):
        self.P2PiloteGroupBox = QtWidgets.QGroupBox("P2 Pilote Control")
        self.P2PiloteGroupBox.setGeometry(0,0,10,10)
        palette = self.P2PiloteGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.P2PiloteGroupBox.setPalette(palette)    
        mainLayout = QtWidgets.QGridLayout()  
    
        mainLayout.setRowStretch(0,2)
        mainLayout.setColumnStretch(0, 1)
        self.P2PiloteGroupBox.setLayout(mainLayout)        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])


    widget = MYP2()
    
    widget.resize(2000, 1000)
    widget.show()

    sys.exit(app.exec())