import sys
import time
import os.path
import threading
import datetime

from ate.tomo import TOMO1S12V2I

from gui.toolsGui import PARAMGUI, SDIGIT, PMLINE, Worker
from gui.p303Gui import PL303GUI

from pickle import NONE
from PySide6.QtCore import SIGNAL, QObject, QTimer
from PySide6 import  QtWidgets, QtGui # -*- coding: utf-8 -*-
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtGui import QColor

import pyqtgraph as pg

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
           
        self.jsonConf = PARAMGUI(project= "Pilote")
       
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

        oneLayout= QtWidgets.QGridLayout()
        oneGroupBox = QtWidgets.QGroupBox("")
        oneGroupBox.setGeometry(0,0,30,30)
        palette = oneGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        oneGroupBox.setPalette(palette)
        oneLayout.addWidget(self.lbllogo,0,0)
        oneLayout.addWidget(self.controlGroupBox,1,0)
        oneLayout.addWidget(self.voltMeterGroupBox,0,2)
        oneLayout.addWidget(self.currentMeterGroupBox,1,2)
        oneLayout.addWidget(self.powerSupply,0,3,3,3)
        
        oneLayout.setRowStretch(2,2)
        oneLayout.setColumnStretch(2, 2)  
        oneGroupBox.setLayout(oneLayout)
        
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.addWidget(oneGroupBox,0, 1)
        self.mainLayout.addWidget(self.P2PiloteGroupBox,1, 1)
        
        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setColumnStretch(1, 1)
        self.centralWidget.setLayout(self.mainLayout)
        
        self.connect(self.btnConnect, SIGNAL("clicked()"),self.initDut)
        self.connect(self.btnEnSeqU, SIGNAL("clicked()"),self.setP2Prog)  
        self.connect(self.btnCal, SIGNAL("clicked()"),self.setCal)        
        
        self.connect(self.btnLogFile, SIGNAL("clicked()"),self.selectLogFile)
        self.connect(self.btnStartStop, SIGNAL("clicked()"),self.startStopLog)  
        self.connect(self.btnPoldePol, SIGNAL("clicked()"),self.polDepol)
        
        self.initPiloteGui()
        self.startThreadReadLine()

        
    def closeEvent(self, event):        
        self.Ilim = self.powerSupply.getI()
        self.Vlim = self.powerSupply.getV()
        self.StatePS = self.powerSupply.getonOff()
        self.saveJsonConf()
        self.stopThreadReadLine()
    
        
    def startThreadReadLine(self):  
        if self.initState == 1:
            try:
                # création de thread
                self.t1 = threading.Thread(target=self.runThreadReadLine)
                self.t1State=1
                self.t1.start()                
                self.timer = QTimer()
                self.timer.setInterval(500)
                self.timer.timeout.connect(self.runtimerPlotrefresh)
                self.timer.start() 
            except:
                self.t1State=0
        
    def stopThreadReadLine(self):
        try: 
            self.timer.stop()
            try:
                self.logFileName.close()  
            except:
                None
            self.t1State=0
            self.t1.join()
        except:
            NONE
               
    def runThreadReadLine(self): 
        idx = 0 
        while(self.t1State==1):
            if self.startLogSate == 1 :  
                try:             
                    ExtStrLine = (str)(self.dut.rLineCom())
                    if len(ExtStrLine) !=0:
                        if ExtStrLine !="OK\r\n":
                            self.t1 = time.time()
                            idx +=1
                            IPS = self.powerSupply.measI()
                            VPS = self.powerSupply.measV()                        
                            fileStr = ""
                            fileStr = str(self.t1)+ ";" + str(self.depolState)+ ";" + str(VPS)+ ";" + str(IPS)+ ";" + ExtStrLine
                            self.ExtractLogFile = open(self.logFileName, "a")
                            self.ExtractLogFile.writelines(fileStr)
                            self.ExtractLogFile.close()                         
                except:
                    self.dut.flushCom() 
                    try:
                        self.ExtractLogFile.close() 
                    except:
                        NONE 
            else:
                idx = 0
                self.dut.flushCom()  
                  
    def runtimerPlotrefresh(self):
        self.powerSupply.displayMeas()
        try:
            NONE
        except:
            NONE
    
    def loadJsonConf(self):
        self.projectName = self.jsonConf.GetJsonParam(name="Project")
        self.depolState = self.jsonConf.GetJsonParam(name="Polarisation_State")
        self.startLogSate = self.jsonConf.GetJsonParam(name="Log_State")
        self.logFileName = self.jsonConf.GetJsonParam(name="CSVfilePath")
        self.Vlim = self.jsonConf.GetJsonParam(name="PL303_Vlim")
        self.Ilim = self.jsonConf.GetJsonParam(name="PL303_Ilim")
        self.StatePS = self.jsonConf.GetJsonParam(name="PL303_State")
        NONE
        
    def saveJsonConf(self):
        self.Ilim = self.powerSupply.getI()
        self.Vlim = self.powerSupply.getV()
        self.StatePS = self.powerSupply.getonOff()
        self.jsonConf.SetJsonParam(name="Project", val=self.projectName)
        self.jsonConf.SetJsonParam(name="Polarisation_State", val=self.depolState)
        self.jsonConf.SetJsonParam(name="Log_State", val=self.startLogSate)
        self.jsonConf.SetJsonParam(name="CSVfilePath", val=self.logFileName)
        self.jsonConf.SetJsonParam(name="PL303_Vlim", val=self.Vlim)
        self.jsonConf.SetJsonParam(name="PL303_Ilim", val=self.Ilim)
        self.jsonConf.SetJsonParam(name="PL303_State", val=self.StatePS)      
    
    def selectLogFile(self):
        self.logDateTime = datetime.datetime.now()
        self.logFileName = "log_p2Pilote_" + "_date-" + str(self.logDateTime)
        file  = QtWidgets.QFileDialog.getSaveFileName(None, "Save a file csv", self.logFileName + ".csv",             "*.csv")
        self.logFileName = file[0]
        self.jsonConf.SetJsonParam(name="CSVfilePath",val=self.logFileName)
        self.ExtractLogFileName = file[0]
        if not os.path.exists(self.ExtractLogFileName):
            self.ExtractLogFile = open(self.ExtractLogFileName, "w")
            self.strLine = "time;polarState;VPS;IPS;TomoIdx;V1;V2;V3;V4;V5;V6;I1;I2;I3;I4;I5;I6\r"
            self.ExtractLogFile.writelines(self.strLine)
            self.ExtractLogFile.close()
        
    def startStopLog(self):
        if self.startLogSate == 0: # start log et acuquiition
            self.btnStartStop.setText("STOP LOG")
            pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
            self.btnStartStop.setPalette(pal)            
            self.startLogSate = 1
            self.dut.startP2Pilote()
        else: # stop
            self.btnStartStop.setText("START LOG")
            pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
            self.btnStartStop.setPalette(pal)
            self.startLogSate = 0
            self.dut.stopP2Pilote()
        
    def polDepol(self):   
        self.tpol = time.time()   
        if self.depolState == 0: # polarisattion state
            self.btnPoldePol.setText("SET DEPOL")
            pal.setColor(QPalette.ButtonText, QColor(231, 140, 49))
            self.btnPoldePol.setPalette(pal)  
            self.powerSupply.SetonOff(state=1)       
            self.depolState = 1   
        else: # polarisattion state
            self.btnPoldePol.setText("SET POL")
            pal.setColor(QPalette.ButtonText, QColor(49, 140, 231))
            self.btnPoldePol.setPalette(pal)
            self.powerSupply.SetonOff(state=0) 
            self.depolState = 0         
        
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
                
    def initPiloteGui(self): 
        self.loadJsonConf()
        self.initDut()
        
        if self.startLogSate == 1: # polarisattion state
            self.btnStartStop.setText("STOP LOG")
            pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
            self.btnStartStop.setPalette(pal)  
            self.dut.startP2Pilote()          
        else: # polarisattion state
            self.btnStartStop.setText("START LOG")
            pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
            self.btnStartStop.setPalette(pal)
            self.dut.stopP2Pilote()
            
        if self.depolState == 1: # polarisation state
            self.btnPoldePol.setText("SET DEPOL")
            pal.setColor(QPalette.ButtonText, QColor(231, 140, 49))
            self.btnPoldePol.setPalette(pal)  
            self.powerSupply.SetonOff(state=1)          
        else: # polarisattion state
            self.btnPoldePol.setText("SET POL")
            pal.setColor(QPalette.ButtonText, QColor(49, 140, 231))
            self.btnPoldePol.setPalette(pal)
            self.powerSupply.SetonOff(state=0)

        self.powerSupply.setVI(v=self.Vlim, i=self.Ilim)
        self.powerSupply.SetonOff(state= self.StatePS)
        self.initState = 1
              
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
                try:          
                    self.displayMeas()
                except:
                    None   
                if self.dut.getP2() == 2:
                    self.btnEnSeqU.setText("Enable TOMO Prg.")
                    self.P2State  = 1
                else:
                    self.P2State  = 0
                    self.btnEnSeqU.setText("Enable P2 Pilote Prg.")
                pal.setColor(QPalette.WindowText, QColor(0, 255, 0))
                self.ledTomo.setPalette(pal)               
            except:
                self.initState = 0
                pal.setColor(QPalette.WindowText, QColor(255, 0, 0))
                self.ledTomo.setPalette(pal)              
            if self.powerSupply.setCom() == 1:
                pal.setColor(QPalette.WindowText, QColor(0, 255, 0))
                self.ledPL303.setPalette(pal)
            else:
                self.initState = 0
                pal.setColor(QPalette.WindowText, QColor(255, 0, 0))
                self.ledPL303.setPalette(pal)
            
            if self.initState == 1:      
                self.btnConnect.setText("Disconnect")
                pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
                self.btnConnect.setPalette(pal) 
        else:
            if self.t1State == 1:
                try:
                    self.stopThreadReadLine()
                except:
                    self.t1State = 0
            del self.dut
            self.initState = 0
            pal.setColor(QPalette.WindowText, QColor(255, 0, 0))
            self.ledPL303.setPalette(pal)
            self.ledTomo.setPalette(pal)                 
            self.btnConnect.setText("CONNECT")
            pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
            self.btnConnect.setPalette(pal)             
    
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
        mainLayout.addWidget(self.btnCal,1,2)
        
        self.btnConnect = QtWidgets.QPushButton("Connect")
        self.btnConnect.setPalette(pal)
        self.btnConnect.setDefault(True)
        mainLayout.addWidget(self.btnConnect,2,2)

        self.ledTomo= QtWidgets.QLabel("Tomo")
        pal.setColor(QPalette.WindowText, QColor(255, 0, 0))
        self.ledTomo.setPalette(pal)
        
        mainLayout.addWidget(self.ledTomo,1,0)
        
        self.ledPL303= QtWidgets.QLabel("PL303")
        self.ledPL303.setPalette(pal)
        mainLayout.addWidget(self.ledPL303,2,0)
        
        lblTask = QtWidgets.QLabel()
        mainLayout.addWidget(lblTask,0, 0)
        lblTask.setText("Switch Tomo1S12V2I to P2.Pilote")
        # Seq Unitai Measure
        self.btnEnSeqU = QtWidgets.QPushButton()
        self.btnEnSeqU.setText("Enable")
        self.btnEnSeqU.setPalette(pal)
        self.btnEnSeqU.setDefault(True)
        mainLayout.addWidget(self.btnEnSeqU,0, 2)               
        
        mainLayout.setRowStretch(2,2)
        mainLayout.setColumnStretch(0, 1)
        self.controlGroupBox.setLayout(mainLayout)
    
   
        
       
    def createVoltMeterGroupBox(self):
        self.voltMeterGroupBox = QtWidgets.QGroupBox("[mV]")
        self.voltMeterGroupBox.setGeometry(0,0,100,50)
        
        palette = self.voltMeterGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.voltMeterGroupBox.setPalette(palette)

        self.vm1 = SDIGIT("V1")
        self.vm2 = SDIGIT("V2")
        self.vm3 = SDIGIT("V3")
        self.vm4 = SDIGIT("V4")
        self.vm5 = SDIGIT("V5")
        self.vm6 = SDIGIT("V6")

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
        self.currentMeterGroupBox = QtWidgets.QGroupBox("[mA]")
        self.currentMeterGroupBox.setGeometry(0,0,100,50)
        
        palette = self.currentMeterGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.currentMeterGroupBox.setPalette(palette)

        self.am1 = SDIGIT("I1")
        self.am2 = SDIGIT("I2")
        self.am3 = SDIGIT("I3")
        self.am4 = SDIGIT("I4")
        self.am5 = SDIGIT("I5")
        self.am6 = SDIGIT("I6")

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
        self.P2PiloteGroupBox = QtWidgets.QGroupBox()
        self.P2PiloteGroupBox.setGeometry(0,0,10,10)
        palette = self.P2PiloteGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.P2PiloteGroupBox.setPalette(palette)    
        mainLayout = QtWidgets.QGridLayout()  
        
        self.btnLogFile = QtWidgets.QPushButton("LogFile")
        self.btnLogFile.setPalette(pal)
        self.btnLogFile.setDefault(True)
        mainLayout.addWidget(self.btnLogFile,0,0)
        
        self.btnStartStop = QtWidgets.QPushButton("START LOG")
        self.btnStartStop.setPalette(pal)
        self.btnStartStop.setDefault(True)
        mainLayout.addWidget(self.btnStartStop,0,1)
        pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
        self.btnStartStop.setPalette(pal)
        
        self.btnPoldePol = QtWidgets.QPushButton("SET POL")
        pal.setColor(QPalette.ButtonText, QColor(49, 140, 231))
        self.btnPoldePol.setPalette(pal)
        self.btnPoldePol.setDefault(True)
        mainLayout.addWidget(self.btnPoldePol,0,4)
      
        self.plotGraph = pg.PlotWidget()
        self.plotGraph.setBackground((53, 53, 53))
        mainLayout.addWidget(self.plotGraph,1,0,1,5)
        time = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 30]
        self.plotGraph.plot(time, temperature)
    
        mainLayout.setRowStretch(0,2)
        mainLayout.setColumnStretch(3, 3)
        self.P2PiloteGroupBox.setLayout(mainLayout)        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])


    widget = MYP2()
    
    widget.resize(2000, 1000)
    widget.show()

    sys.exit(app.exec())