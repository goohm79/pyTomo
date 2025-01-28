import sys
import serial.tools.list_ports
import time
from ImgDrawer import ImgDrawer
from timeloop import Timeloop
from datetime import timedelta
from PySide6.QtCore import SIGNAL, QObject, QThread, QTimer
from PySide6 import QtCore, QtWidgets, QtGui # -*- coding: utf-8 -*-
from PySide6.QtGui import QPalette, QColor, QPixmap
from tomo import TOMO1S12V2I
from tomoWaterFlow import TOMOWATERFLOW
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



class DIRECTION(QtWidgets.QWidget):
    def __init__(self):
        
        self.GroupBox = QtWidgets.QGroupBox("Direction")
        self.GroupBox.setGeometry(0,0,100,100)
            
        palette = self.GroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        
        
    
        self.b1= QtWidgets.QRadioButton("⬅️ LEFT ")
        self.b1.toggled.connect(lambda:self.setDir("left"))
        self.b1.setStyleSheet("QRadioButton::indicator::checked"
                                        "{"
                                        "background-color : red"
                                        "}")
        self.b1.setPalette(pal)
        
        self.b2 = QtWidgets.QRadioButton("UP ⬆️")
        
        self.b2.toggled.connect(lambda:self.setDir("up"))
        self.b2.setStyleSheet("QRadioButton::indicator::checked"
                                        "{"
                                        "background-color : green"
                                        "}")
        self.b2.setPalette(pal)
            
        self.b3 = QtWidgets.QRadioButton("⬇️ DOWN ")
        self.direction = "down"
        self.b3.setChecked(True)
        self.b3.toggled.connect(lambda:self.setDir("down"))
        self.b3.setStyleSheet("QRadioButton::indicator::checked"
                                        "{"
                                        "background-color : orange"
                                        "}")
        self.b3.setPalette(pal)
        
        self.b4 = QtWidgets.QRadioButton("RIGHT ➡️")
        self.b4.toggled.connect(lambda:self.setDir("right"))
        self.b4.setStyleSheet("QRadioButton::indicator::checked"
                                        "{"
                                        "background-color : yellow"
                                        "}")
        self.b4.setPalette(pal)
        
       
        self.GroupBox.setPalette(palette)
        mainLayout = QtWidgets.QGridLayout()    
        mainLayout.addWidget(self.b1,0, 0)
        mainLayout.addWidget(self.b2,0, 1)
        mainLayout.addWidget(self.b3,0, 2)
        mainLayout.addWidget(self.b4,0, 3)
        self.GroupBox.setLayout(mainLayout)
        
    def setDir(self,b):
        self.direction = b
        
    def getDir(self):
        return self.direction
                    
class DIGIT(QtWidgets.QWidget):
    def __init__(self, name = ""):
        self.name = name
        
        self.GroupBox = QtWidgets.QGroupBox("")
        self.GroupBox.setGeometry(0,0,30,30)
        
        palette = self.GroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.GroupBox.setPalette(palette)
        
        self.lbl = QtWidgets.QLabel()        
        self.lbl.setText(self.name)

        # get the palette
        palette = self.lbl.palette()
        # foreground color
        palette.setColor(QPalette.WindowText, QtGui.QColor(49, 140, 231))
        self.lbl.setPalette(palette)

         
        self.lcd = QtWidgets.QLCDNumber()
        self.lcd.setGeometry(0,0,30,30) 
        self.lcd.setSegmentStyle(self.lcd.SegmentStyle.Flat)  
        # get the palette
        palette = self.lcd.palette()
        # foreground color
        palette.setColor(QPalette.WindowText, QtGui.QColor(49, 140, 231))
        # background color
        palette.setColor(QPalette.Light, QtGui.QColor(53, 53, 53))  # "light" border
        palette.setColor(QPalette.Dark, QtGui.QColor(53, 53, 53)) # "dark" border
        
        self.lcd.setPalette(palette)    
        self.lcd.display(0)
        
        self.check = QtWidgets.QCheckBox()
        self.check.setChecked(True)
        self.check.setPalette(pal)  
        
        mainLayout = QtWidgets.QGridLayout()
        
        mainLayout.addWidget(self.lbl,0, 0)
        mainLayout.addWidget(self.check,0,1)
        mainLayout.addWidget(self.lcd,1, 0, 1, 1)
        mainLayout.setRowStretch(1,1)
        self.GroupBox.setLayout(mainLayout)
    
    def checkState(self):
        print(str(self.check.checkState()))
        if self.check.isChecked():
            return True
        else:
            return False
    
class PMLINE(QtWidgets.QWidget):
    def __init__(self, name = "", delta = 1.0):
        self.name = name
        self.delta = delta
        self.value = 0.0
        self.GroupBox = QtWidgets.QGroupBox(self.name)
        self.GroupBox.setGeometry(0,0,25,100)
        palette = self.GroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.GroupBox.setPalette(palette)
        
        mainLayout = QtWidgets.QGridLayout()
        
        self.lbl = QtWidgets.QLabel() 
        self.lbl.setText("X")     
        self.lbl.setGeometry(0,0,25,25)
        palette = self.lbl.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))
        self.lbl.setPalette(palette)
        
        self.inputbox = QtWidgets.QLineEdit()
        self.inputbox.setGeometry(0,0,25,25)
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(60, 60, 60))
        pal.setColor(QPalette.Button, QColor(60, 60, 60))
        pal.setColor(QPalette.Text, QColor(255, 255, 255))
        self.inputbox.setPalette(pal)      
        
        self.setVal(self.value)
        
        self.p = QtWidgets.QPushButton("+")
        self.p.setGeometry(0,0,25,25)
        self.p.setPalette(pal)
        self.p.setDefault(True)
        self.p.clicked.connect(lambda:self.btnP())

        self.m = QtWidgets.QPushButton("-")
        self.m.setGeometry(0,0,25,25)
        self.m.setPalette(pal)
        self.m.setDefault(True)
        self.m.clicked.connect(lambda:self.btnM())
 
        mainLayout.addWidget(self.m ,0, 1)
        mainLayout.addWidget(self.inputbox ,0, 2)
        mainLayout.addWidget(self.p ,0, 3)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setColumnStretch(2, 3)
        self.GroupBox.setLayout(mainLayout)
    
    def btnP(self):
        self.value = self.getVal() + self.delta 
        self.setVal(self.value)
        
    def btnM(self):
        self.value = self.getVal() - self.delta 
        self.setVal(self.value)
        
    def setVal(self, val):
        self.value = val
        self.inputbox.setText("{0:.3f}".format(self.value))
        
    def getVal(self):
        self.value = float(self.inputbox.text())
        return self.value

class Worker(QObject):
    finished = SIGNAL
    progress = SIGNAL

    def run(self):
        """Long-running task."""
        while(True):
            time.sleep(1)
            self.progress.emit()
    
    def stop(self):
        self.finished.emit()
        
        
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
        self.createCurrentMeterGroupBox()
        self.createControlGroupBox()
        self.createTerminalGroupBox()
     

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
        oneLayout.addWidget(self.controlGroupBox,0,0,0,1)
        oneLayout.addWidget(self.terminalGroupBox,0,1,0,1)
        oneLayout.addWidget(self.voltMeterGroupBox,0,2)
        oneLayout.addWidget(self.currentMeterGroupBox,1,2)
        oneLayout.addWidget(self.lbllogo,0,3)
        oneLayout.setRowStretch(0,0)
        oneLayout.setColumnStretch(1, 1)  
        oneGroupBox.setLayout(oneLayout)
        
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.addWidget(oneGroupBox,0, 1)
        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setColumnStretch(1, 1)
        self.centralWidget.setLayout(self.mainLayout)
        
        self.connect(self.btnConnect, SIGNAL("clicked()"),self.initDut)
        self.connect(self.btnComList, SIGNAL("clicked()"),self.listPortCom)
        self.connect(self.btnEnSeqU, SIGNAL("clicked()"),self.setP2Prog)  
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
        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])


    widget = MYP2()
    
    widget.resize(2000, 1000)
    widget.show()

    sys.exit(app.exec())