import sys
import serial.tools.list_ports
import time

from ate.tomo import TOMO1S12V2I
from ate.PL303P import PL303
from gui.toolsGui import DIGIT, DIRECTION, PMLINE, Worker
from ate.ImgDrawer import ImgDrawer

from timeloop import Timeloop
from datetime import timedelta
from PySide6.QtCore import SIGNAL, QObject, QThread, QTimer
from PySide6 import QtCore, QtWidgets, QtGui # -*- coding: utf-8 -*-
from PySide6.QtGui import QPalette, QColor, QPixmap

from pickle import NONE

from PySide6.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QMainWindow
from PySide6.QtCore import Qt, QRect, QRectF
from PySide6.QtGui import QBrush, QPen, QColor, QPainter

import os.path

import threading
import datetime

LARGEURCHARIOT = 1.52  # largeur chariot
NWHEEL = 6        #nombre de roue
ESPACEWHEEL= 0.23 #espace entre chacune roue ectrochimique  en metre
DISTWHEEL = 0.09695  #périmètre/4 roue odometre en metre
VITESSEMAX = 3.5

AWHEELCOEF = float((ESPACEWHEEL * (NWHEEL-1))) / 2.0      #coeaf A

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
        self.setWindowTitle('p2GUI.py')
         # Now use a palette to switch to dark colors:
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText,QtGui.QColor(0, 0, 0))
        app.setPalette(palette)      
        
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        
        self.createVoltMeterGroupBox()
        self.createControlGroupBox()
        self.createTerminalGroupBox()
        self.createCmdGroupBox()

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
        self.wheelSize = DISTWHEEL
        self.WheelDist = ESPACEWHEEL
        self.ActiveWheel = []

        oneLayout= QtWidgets.QGridLayout()
        oneGroupBox = QtWidgets.QGroupBox("")
        oneGroupBox.setGeometry(0,0,30,30)
        palette = oneGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        oneGroupBox.setPalette(palette)
        oneLayout.addWidget(self.controlGroupBox,0, 0)
        oneLayout.addWidget(self.terminalGroupBox,0,1)
        oneLayout.addWidget(self.voltMeterGroupBox,0,2)
        oneLayout.addWidget(self.lbllogo,0,3)
        oneLayout.setRowStretch(0,0)
        oneLayout.setColumnStretch(1, 1)  
        oneGroupBox.setLayout(oneLayout)
        
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.addWidget(oneGroupBox,0, 1)
        self.mainLayout.addWidget(self.cmdGroupBox,1,1)
        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setColumnStretch(1, 1)
        self.centralWidget.setLayout(self.mainLayout)
        
        self.connect(self.btnConnect, SIGNAL("clicked()"),self.initDut)
        self.connect(self.btnComList, SIGNAL("clicked()"),self.listPortCom)
        self.connect(self.btnEnSeqU, SIGNAL("clicked()"),self.setP2Prog)
        self.connect(self.btnStartStop, SIGNAL("clicked()"),self.setStartStop)
        self.connect(self.btnPause, SIGNAL("clicked()"),self.setPause)    
        self.connect(self.btnCal, SIGNAL("clicked()"),self.setCal)
        #self.connect(self.btnMeas, SIGNAL("clicked()"),self.displayMeas)
        self.listPortCom()
        #self.setCentralWidget(oneGroupBox)
        
    def __del__(self):
        self.stopThreadReadLine()
        del self.dut
    
        
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
        count = 0    
        while(self.t1State==1):
            if self.pause != 1 :  
                try:             
                    ExtStrLine = (str)(self.dut.rLineCom())
                    if len(ExtStrLine) !=0:
                        self.t1 = time.time()
                        self.dt = self.t1 - self.t2
                        self.t2 = self.t1
                        self.vitesse = 3.6 * ESPACEWHEEL / self.dt 
                        if self.vitesse < VITESSEMAX:
                            self.lblvitesse.setPalette(pal)
                        else:
                            self.lblvitesse.setPalette(palRed)
                        self.lblvitesse.setText(str("{0:.2f}".format(self.vitesse)) + " Km/h") 
                        print(str(self.vitesse))
                        self.getActiveWheel()
                        print(str(self.ActiveWheel))
                        self.x = self.xcolumn.getVal()
                        self.y = self.ycolumn.getVal()
                        tabDatas = ExtStrLine[:-2].split(';')
                        fileStr = ""
                        self.ExtractLogFile = open(self.ExtractLogFileName, "a")
                        if self.dir.direction == "right":
                            self.x = self.x + self.wheelSize
                            self.xcolumn.setVal(self.x)  
                            for i in range(NWHEEL):
                                if self.ActiveWheel[i] == True:
                                    yWheel = self.y + (i*self.WheelDist)-AWHEELCOEF
                                    n = i+1
                                    fileStr = str(self.stage.getVal())+ ";" + self.inputboxZone.text()+ ";" + self.dir.direction + ";" + str("{0:.3f}".format(self.x)) + ";" + str("{0:.3f}".format(yWheel)) + ";" + tabDatas[n]   + "\r" 
                                    self.ExtractLogFile.writelines(fileStr)  
                                    self.view.set(float(self.x), float(yWheel), float(tabDatas[n]))
                                
                        elif self.dir.direction == "left":
                            self.x = self.x - self.wheelSize
                            self.xcolumn.setVal(self.x)  
                            for i in range(NWHEEL):
                                if self.ActiveWheel[i] == True:
                                    yWheel = self.y + (((NWHEEL-1-i)*self.WheelDist)-AWHEELCOEF)
                                    n = i+1
                                    fileStr = str(self.stage.getVal()) + ";" + self.inputboxZone.text()+ ";"  + self.dir.direction + ";" +  str("{0:.3f}".format(self.x)) + ";" + str("{0:.3f}".format(yWheel)) + ";" + tabDatas[n]   + "\r" 
                                    self.ExtractLogFile.writelines(fileStr)   
                                    self.view.set(float(self.x), float(yWheel), float(tabDatas[n]))
                                           
                        elif self.dir.direction == "up":
                            self.y = self.y - self.wheelSize
                            self.ycolumn.setVal(self.y)
                            for i in range(NWHEEL):
                                if self.ActiveWheel[i] == True:
                                    xWheel = self.x + (i*self.WheelDist)-AWHEELCOEF
                                    n = i+1
                                    fileStr = str(self.stage.getVal()) + ";" + self.inputboxZone.text()+ ";" + self.dir.direction + ";" +  str("{0:.3f}".format(xWheel)) + ";" + str("{0:.3f}".format(self.y)) + ";" + tabDatas[n] + "\r"  
                                    self.ExtractLogFile.writelines(fileStr)
                                    self.view.set(float(xWheel), float(self.y), float(tabDatas[n]))
                                             
                        elif self.dir.direction == "down":
                            self.y = self.y + self.wheelSize
                            self.ycolumn.setVal(self.y)
                            for i in range(NWHEEL):
                                if self.ActiveWheel[i] == True:
                                    xWheel = self.x + (((NWHEEL-1-i)*self.WheelDist)-AWHEELCOEF)
                                    n = i+1
                                    fileStr = str(self.stage.getVal()) + ";" + self.inputboxZone.text()+ ";" + self.dir.direction + ";" +  str("{0:.3f}".format(xWheel)) + ";" + str("{0:.3f}".format(self.y)) + ";" + tabDatas[n]  + "\r"   
                                    self.ExtractLogFile.writelines(fileStr)   
                                    self.view.set( float(xWheel), float(self.y), float(tabDatas[n]))
                                     
                        self.ExtractLogFile.close()  
                        self.vm1.lcd.display(float(tabDatas[1]))
                        self.vm2.lcd.display(float(tabDatas[2]))
                        self.vm3.lcd.display(float(tabDatas[3]))
                        self.vm4.lcd.display(float(tabDatas[4]))
                        self.vm5.lcd.display(float(tabDatas[5]))
                        self.vm6.lcd.display(float(tabDatas[6]))
                        print(ExtStrLine)
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
            self.view.saveImage()
            self.view.loadImage()
        except:
            NONE
               
    def setStartStop(self):
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(60, 60, 60))
        pal.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))  
        pal.setColor(QPalette.Button, QColor(60, 60, 60))
        pal.setColor(QPalette.Text, QColor(255, 255, 255))
        
        if self.start == 0:
            self.start =1
            self.btnStartStop.setText("STOP")
            pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
            self.btnStartStop.setPalette(pal)
            self.startThreadReadLine()
        else:
            self.start = 0
            self.btnStartStop.setText("START")
            pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
            self.btnStartStop.setPalette(pal)
            try:
                self.stopThreadReadLine()
            except:
                None
    
    def getActiveWheel(self):
        self.ActiveWheel = []
        self.ActiveWheel.append(self.vm1.checkState())
        self.ActiveWheel.append(self.vm2.checkState())
        self.ActiveWheel.append(self.vm3.checkState())
        self.ActiveWheel.append(self.vm4.checkState())
        self.ActiveWheel.append(self.vm5.checkState())
        self.ActiveWheel.append(self.vm6.checkState())
        
              
    def setPause(self):
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(60, 60, 60))
        pal.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))  
        pal.setColor(QPalette.Button, QColor(60, 60, 60))
        pal.setColor(QPalette.Text, QColor(255, 255, 255))
        
        if self.pause ==0 :
            self.pause =1
            self.btnPause.setText("RESUME")
            pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
            self.btnPause.setPalette(pal)
        else:
            self.pause =0
            self.btnPause.setText("PAUSE")
            pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
            self.btnPause.setPalette(pal)
        
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
            portCOM = str(self.listboxCom.currentText())
            self.dut = TOMO1S12V2I(comPort=portCOM)
            self.btnConnect.setText("Disconnect")
            pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
            self.btnConnect.setPalette(pal)
            self.textEditTerminal.setText("Connected to: " + portCOM)
            self.dut.setPwr(pwrIV=1, pwrS=1, pwrS33V=1)
            self.textEditTerminal.append("Set power On")
            self.displayMeas()
            if self.dut.getP2() == 1:
                self.btnEnSeqU.setText("Enable TOMO Prg.")
                self.P2State  = 1
            else:
                self.P2State  = 0
                self.btnEnSeqU.setText("Enable P2 Prg.")
            self.initState = 1
        else:
            if self.t1State == 1:
                try:
                    self.stopThreadReadLine()
                except:
                    self.t1State = 0
            del self.dut
            self.initState = 0
            self.btnConnect.setText("CONNECT")
            pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
            self.btnConnect.setPalette(pal)
            self.textEditTerminal.setText("COM PORT disconnected")
            
        
    def listPortCom(self):
        lCom = list(serial.tools.list_ports.comports())
        self.listboxCom.clear()
        for item in lCom:
            self.listboxCom.addItem(str(item.device))
     
    
    def getMainTaskState(self):
        if self.dut.su_getMainTask() ==1 : 
            self.btnEnSeqU.setText("SeqU STOP")
            self.t1State = 1
        else:
            self.t1State = 0
                  
            
    def displayMeas(self):
        if self.t1State == 0:
            self.textEditTerminal.append("Get measure")
            self.dut.setAcquire()
            self.vm1.lcd.display(self.dut.getMeas("V1"))
            self.vm2.lcd.display(self.dut.getMeas("V2"))
            self.vm3.lcd.display(self.dut.getMeas("V3"))
            self.vm4.lcd.display(self.dut.getMeas("V4"))
            self.vm5.lcd.display(self.dut.getMeas("V5"))
            self.vm6.lcd.display(self.dut.getMeas("V6"))
        
            
    
    def createTerminalGroupBox(self):
        
        self.terminalGroupBox = QtWidgets.QGroupBox("Terminal")
        self.terminalGroupBox.setGeometry(0,0,30,10)
        self.terminalGroupBox.setPalette(pal)
        mainLayout = QtWidgets.QGridLayout()  
       
        # cmd line
        self.textEditTerminal = QtWidgets.QTextEdit()  
        self.textEditTerminal.setText("")
        self.textEditTerminal.setPalette(pal)
        
       # mainLayout.setRowStretch(1, 1)
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
      
        # Com    
        self.listboxCom = QtWidgets.QComboBox()
        self.listboxCom.setPalette(pal)
         #self.listboxCom.insertItem(0, "/dev/ttyACM0")       
        
        self.lblSuCom = QtWidgets.QLabel() 
        self.lblSuCom.setText("ComPort")     
        palette = self.lblSuCom.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblSuCom.setPalette(palette)
        
       # mainLayout.addWidget(self.lblSuCom,0, 0)
        mainLayout.addWidget(self.listboxCom,0, 1)

          # Refresh listcom
        self.btnComList = QtWidgets.QPushButton("ComPort LIST")
        self.btnComList.setPalette(pal)
        self.btnComList.setDefault(True)
        mainLayout.addWidget(self.btnComList,0, 0)
        
        self.btnCal = QtWidgets.QPushButton("CALIBRATION")
        self.btnCal.setPalette(pal)
        self.btnCal.setDefault(True)
        mainLayout.addWidget(self.btnCal,2,0)
        
        # self.btnMeas = QtWidgets.QPushButton("Get MEASURE")
        # self.btnMeas.setDefault(True)
        # self.btnMeas.setPalette(pal)
        # mainLayout.addWidget(self.btnMeas,2, 1)

        lblTask = QtWidgets.QLabel()
        mainLayout.addWidget(lblTask,3, 0)
        lblTask.setText("Switch Tomo1S12V2I to P2")
         # Seq Unitai Measure
        self.btnEnSeqU = QtWidgets.QPushButton()
        self.btnEnSeqU.setText("Enable")
        self.btnEnSeqU.setPalette(pal)
        self.btnEnSeqU.setDefault(True)
        
        # Init Comport
        self.btnConnect = QtWidgets.QPushButton("CONNECT")
        self.btnConnect.setDefault(True)
        pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
        self.btnConnect.setPalette(pal)
        mainLayout.addWidget(self.btnConnect,1, 1)
        
        mainLayout.addWidget(self.btnEnSeqU,3, 1)
        mainLayout.setRowStretch(2,2)
        mainLayout.setColumnStretch(0, 1)
        self.controlGroupBox.setLayout(mainLayout)
    
    def createCmdGroupBox(self):
       
        
        pal2 = pal
        self.cmdGroupBox = QtWidgets.QGroupBox()
        self.cmdGroupBox.setGeometry(0,0,300,300)
        
        palette = self.cmdGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.cmdGroupBox.setPalette(palette)

        self.stage = PMLINE(name="Etage", delta=1.0)
        self.xcolumn = PMLINE(name="Position: X (m)",delta=LARGEURCHARIOT)
        self.ycolumn = PMLINE(name="& Y (m)", delta=LARGEURCHARIOT)
        self.dir=DIRECTION()
        self.btnStartStop = QtWidgets.QPushButton("START")
        self.btnStartStop.setGeometry(QtCore.QRect(340, 30, 23, 20))
        pal2.setColor(QPalette.ButtonText, QColor(0, 255, 0))
        self.btnStartStop.setPalette(pal)
        self.btnStartStop.setDefault(True)
        self.btnPause = QtWidgets.QPushButton("PAUSE")
        self.btnPause.setGeometry(QtCore.QRect(340, 30, 23, 20))
        pal2.setColor(QPalette.ButtonText, QColor(255, 0, 0))
        self.btnPause.setPalette(pal2)
        self.btnPause.setDefault(True)
        
        self.GBZone = QtWidgets.QGroupBox("Zone definition")
        self.GBZone.setGeometry(0,0,25,100)
        self.GBZone.setPalette(pal)
        GBZoneLayout = QtWidgets.QGridLayout()        
        self.inputboxZone = QtWidgets.QLineEdit()
        self.inputboxZone.setGeometry(0,0,25,25)
        GBZoneLayout.addWidget(self.inputboxZone ,0, 0)
        self.GBZone.setLayout(GBZoneLayout)

        self.lblGoOhm = QtWidgets.QLabel() 
        self.lblGoOhm.setText("design by GoOHM")     
        self.lblGoOhm.setGeometry(0,0,25,25)
        self.lblGoOhm.setPalette(pal)
        
        self.lblvitesse = QtWidgets.QLabel() 
        self.lblvitesse.setText("Km/h")     
        self.lblvitesse.setGeometry(0,0,25,25)
        self.lblvitesse.setPalette(pal)
       
        self.view = ImgDrawer()
        self.view.resize(1000, 600) 
        
        mainLayout = QtWidgets.QGridLayout()
        
        oneGroupBox = QtWidgets.QGroupBox("")
        oneGroupBox.setGeometry(0,0,300,300)
        oneLayout = QtWidgets.QGridLayout()
        oneLayout.addWidget(self.stage.GroupBox,0, 0)
        oneLayout.addWidget(self.GBZone,0, 1)
        oneLayout.addWidget(self.xcolumn.GroupBox,0, 3)
        oneLayout.addWidget(self.ycolumn.GroupBox,0, 4)
        oneLayout.addWidget(self.dir.GroupBox,0, 2)
        oneLayout.setRowStretch(1, 1)
        oneLayout.setColumnStretch(2, 2)
        oneGroupBox.setLayout(oneLayout)
        
        secGroupBox = QtWidgets.QGroupBox("")
        secGroupBox.setGeometry(0,0,300,300)
        secLayout = QtWidgets.QGridLayout()
        secLayout.addWidget(self.btnStartStop,0, 0)
       
        secLayout.addWidget(self.btnPause,0, 2) 
        secLayout.addWidget(self.lblvitesse,1,0) 
        secLayout.addWidget(self.lblGoOhm,1, 2)
        secLayout.setRowStretch(0,0)       
        secLayout.setColumnStretch(1,1)
        secGroupBox.setLayout(secLayout)
        
        mainLayout.addWidget(oneGroupBox,0,0)
        mainLayout.addWidget(self.view,1,0)
        mainLayout.addWidget(secGroupBox,2, 0)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setColumnStretch(1, 1)
        self.cmdGroupBox.setLayout(mainLayout)
        
        
        
       
    def createVoltMeterGroupBox(self):
        self.voltMeterGroupBox = QtWidgets.QGroupBox("VoltMeters  [mV]")
        self.voltMeterGroupBox.setGeometry(0,0,100,50)
        
        palette = self.voltMeterGroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.voltMeterGroupBox.setPalette(palette)

        self.vm1 = DIGIT("Channel 1")
        self.vm2 = DIGIT("Channel 2")
        self.vm3 = DIGIT("Channel 3")
        self.vm4 = DIGIT("Channel 4")
        self.vm5 = DIGIT("Channel 5")
        self.vm6 = DIGIT("Channel 6")

        mainLayout = QtWidgets.QGridLayout()
        
        mainLayout.addWidget(self.vm1.GroupBox,0, 1)
        mainLayout.addWidget(self.vm2.GroupBox,0, 2)
        mainLayout.addWidget(self.vm3.GroupBox,0, 3)
        mainLayout.addWidget(self.vm4.GroupBox,0, 4)
        mainLayout.addWidget(self.vm5.GroupBox,0, 5)
        mainLayout.addWidget(self.vm6.GroupBox,0, 6)
        mainLayout.setRowStretch(0,0)
        self.voltMeterGroupBox.setLayout(mainLayout)
            
if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    app.shutdown()
    app = QtWidgets.QApplication([])
    widget = MYP2()
    
    widget.resize(2000, 1000)
    widget.show()

    sys.exit(app.exec())