import sys
import serial.tools.list_ports
import time
from timeloop import Timeloop
from datetime import timedelta
from PySide6.QtCore import SIGNAL
from PySide6 import QtCore, QtWidgets, QtGui # -*- coding: utf-8 -*-
from PySide6.QtGui import QPalette, QColor, QPixmap
from tomo import TOMO1S12V2I
from tomoWaterFlow import TOMOWATERFLOW
from pickle import NONE

from PySide6.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem
from PySide6.QtCore import Qt, QRect, QRectF
from PySide6.QtGui import QBrush, QPen, QColor, QPainter

import os.path
from tkinter import filedialog
import threading

class DIRECTION(QtWidgets.QWidget):
    def __init__(self):
        self.direction = ""
        self.GroupBox = QtWidgets.QGroupBox("Direction")
        self.GroupBox.setGeometry(0,0,100,100)
            
        palette = self.GroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.GroupBox.setPalette(palette)
    
        self.b1= QtWidgets.QRadioButton("⬅️ LEFT ")
        self.b1.toggled.connect(lambda:self.setDir("left"))
        
        self.b2 = QtWidgets.QRadioButton("UP ⬆️")
        self.b2.setChecked(True)
        self.b2.toggled.connect(lambda:self.setDir("up"))
            
        self.b3 = QtWidgets.QRadioButton("⬇️ DOWN ")
        self.b3.toggled.connect(lambda:self.setDir("down"))
        
        self.b4 = QtWidgets.QRadioButton("RIGHT ➡️")
        self.b4.toggled.connect(lambda:self.setDir("right"))
        
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
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.GroupBox.setPalette(palette)
        
        self.lbl = QtWidgets.QLabel()        
        self.lbl.setText(self.name)

        # get the palette
        palette = self.lbl.palette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(49, 140, 231))
        self.lbl.setPalette(palette)

         
        self.lcd = QtWidgets.QLCDNumber()
        self.lcd.setGeometry(0,0,30,30) 
        self.lcd.setSegmentStyle(self.lcd.SegmentStyle.Flat)  
        # get the palette
        palette = self.lcd.palette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(49, 140, 231))
        # background color
        palette.setColor(palette.Light, QtGui.QColor(53, 53, 53))  # "light" border
        palette.setColor(palette.Dark, QtGui.QColor(53, 53, 53)) # "dark" border
        
        self.lcd.setPalette(palette)    
        self.lcd.display(0)
        mainLayout = QtWidgets.QGridLayout()
        
        mainLayout.addWidget(self.lbl,0, 0)
        mainLayout.addWidget(self.lcd,1, 0)
        mainLayout.setRowStretch(1, 1)
        self.GroupBox.setLayout(mainLayout)
    
class PMLINE(QtWidgets.QWidget):
    def __init__(self, name = ""):
        self.name = name
        self.name = name
        self.value = 0.0
        self.GroupBox = QtWidgets.QGroupBox(self.name)
        self.GroupBox.setGeometry(0,0,25,100)
        palette = self.GroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.GroupBox.setPalette(palette)
        
        mainLayout = QtWidgets.QGridLayout()
        
        self.lbl = QtWidgets.QLabel() 
        self.lbl.setText("X")     
        self.lbl.setGeometry(0,0,25,25)
        palette = self.lbl.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lbl.setPalette(palette)
        
        self.inputbox = QtWidgets.QLineEdit()
        self.inputbox.setGeometry(0,0,25,25)
        self.setVal(self.value)
        
        self.p = QtWidgets.QPushButton("+")
        self.p.setGeometry(0,0,25,25)
        self.p.setDefault(True)
        self.p.clicked.connect(lambda:self.btnP())

        self.m = QtWidgets.QPushButton("-")
        self.m.setGeometry(0,0,25,25)
        self.m.setDefault(True)
        self.m.clicked.connect(lambda:self.btnM())
 
        mainLayout.addWidget(self.m ,0, 1)
        mainLayout.addWidget(self.inputbox ,0, 2)
        mainLayout.addWidget(self.p ,0, 3)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setColumnStretch(2, 3)
        self.GroupBox.setLayout(mainLayout)
    
    def btnP(self):
        self.value = self.getVal() + 1.0
        self.setVal(self.value)
        
    def btnM(self):
        self.value = self.getVal() - 1.0
        self.setVal(self.value)
        
    def setVal(self, val):
        self.value = val
        self.inputbox.setText(str(self.value)) 
        
    def getVal(self):
        self.value = float(self.inputbox.text())
        return self.value

class MYP2(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('P2')
         # Now use a palette to switch to dark colors:
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText,QtGui.QColor(0, 0, 0))
        app.setPalette(palette)      
        
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
    
        oneLayout= QtWidgets.QGridLayout()
        oneGroupBox = QtWidgets.QGroupBox("")
        oneGroupBox.setGeometry(0,0,30,30)
        palette = oneGroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        oneGroupBox.setPalette(palette)
        oneLayout.addWidget(self.controlGroupBox,0, 0)
        oneLayout.addWidget(self.terminalGroupBox,0,1)
        oneLayout.addWidget(self.voltMeterGroupBox,0,2)
        oneLayout.addWidget(self.lbllogo,0,3)
        oneLayout.setRowStretch(1, 1)
        oneLayout.setColumnStretch(1, 1)  
        oneGroupBox.setLayout(oneLayout)
        
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.addWidget(oneGroupBox,0, 1)
        self.mainLayout.addWidget(self.cmdGroupBox,1,1)
        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setColumnStretch(1, 1)
        self.setLayout(self.mainLayout)
        
        self.connect(self.btnConnect, SIGNAL("clicked()"),self.initDut)
        self.connect(self.btnComList, SIGNAL("clicked()"),self.listPortCom)
        self.connect(self.btnEnSeqU, SIGNAL("clicked()"),self.setP2Prog)
        self.connect(self.btnStartStop, SIGNAL("clicked()"),self.setStartStop)
        self.connect(self.btnPause, SIGNAL("clicked()"),self.setPause)    
        self.listPortCom()
        
    def __del__(self):
        self.stopThreadReadLine()
        del self.dut
        
    def startThreadReadLine(self):  
        if self.initState == 1:
            try:
                file  = QtWidgets.QFileDialog.getSaveFileName(self)
                self.ExtractLogFileName = file[0]
                self.ExtractLogFile = open(self.ExtractLogFileName, "w")
                self.strLine = "Index;Time;Type;Polarité;Channel;Tu;ActiveZone;Isource;Vsource;V1,V2,V3,V4,V5,V6,V7,V8,V9,V10,V11,V12,I1,I2\n\r"
                self.ExtractLogFile.writelines(self.strLine)
                self.ExtractLogFile.close()
                # création de thread
                self.t1 = threading.Thread(target=self.printThreadReadLine)
                self.t1State=1
                self.t1.start()
                
            except:
                self.t1State=0
        
    def stopThreadReadLine(self):
        self.t1State=0
        self.t1.join()
               
    def printThreadReadLine(self):   
        while(self.t1State==1):
            ExtStrLine = (str)(self.dut.rLineCom())
            self.ExtractLogFile = open(self.ExtractLogFileName, "a")
            self.ExtractLogFile.writelines(ExtStrLine)
            self.ExtractLogFile.close()
            print(ExtStrLine)
            
    def setStartStop(self):
        None
    def setPause(self):
        None
        
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
        if self.initState == 0:
            portCOM = str(self.listboxCom.currentText())
            self.dut = TOMO1S12V2I(comPort=portCOM)
            self.btnConnect.setText("Disconnect")
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
        self.terminalGroupBox.setGeometry(0,0,30,30)
        palette = self.terminalGroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.terminalGroupBox.setPalette(palette)
        mainLayout = QtWidgets.QGridLayout()  
       
        # cmd line
        self.textEditTerminal = QtWidgets.QTextEdit()  
        self.textEditTerminal.setText("")
        
       # mainLayout.setRowStretch(1, 1)
        mainLayout.addWidget(self.textEditTerminal,0, 0)
        mainLayout.setRowStretch(0, 1)
        mainLayout.setColumnStretch(0, 1)
        self.terminalGroupBox.setLayout(mainLayout)
    
              
    def createControlGroupBox(self):
        self.controlGroupBox = QtWidgets.QGroupBox("Control")
        self.controlGroupBox.setGeometry(0,0,10,10)
        palette = self.controlGroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.controlGroupBox.setPalette(palette)
        
        mainLayout = QtWidgets.QGridLayout()  
        
        # Com    
        self.listboxCom = QtWidgets.QComboBox()
         #self.listboxCom.insertItem(0, "/dev/ttyACM0")       
        
        self.lblSuCom = QtWidgets.QLabel() 
        self.lblSuCom.setText("ComPort")     
        palette = self.lblSuCom.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblSuCom.setPalette(palette)
        
       # mainLayout.addWidget(self.lblSuCom,0, 0)
        mainLayout.addWidget(self.listboxCom,0, 1)
        
        # Init Comport
        self.btnConnect = QtWidgets.QPushButton("CONNECT")
        self.btnConnect.setDefault(True)
        mainLayout.addWidget(self.btnConnect,1, 1)
        
          # Refresh listcom
        self.btnComList = QtWidgets.QPushButton("ComPort LIST")
        self.btnComList.setDefault(True)
        mainLayout.addWidget(self.btnComList,0, 0)
  
        lblTask = QtWidgets.QLabel()
        mainLayout.addWidget(lblTask,2, 0)
        lblTask.setText("Switch Tomo1S12V2I to P2")
         # Seq Unitai Measure
        self.btnEnSeqU = QtWidgets.QPushButton()
        self.btnEnSeqU.setText("Enable")
        self.btnEnSeqU.setDefault(True)
        mainLayout.addWidget(self.btnEnSeqU,2, 1)
        mainLayout.setRowStretch(0, 1)
        mainLayout.setColumnStretch(0, 1)
        self.controlGroupBox.setLayout(mainLayout)
    
    def createCmdGroupBox(self):
        self.cmdGroupBox = QtWidgets.QGroupBox("Map")
        self.cmdGroupBox.setGeometry(0,0,300,300)
        
        palette = self.cmdGroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.cmdGroupBox.setPalette(palette)

        self.stage = PMLINE("Etage")
        self.xcolumn = PMLINE("Position: X (m)")
        self.ycolumn = PMLINE("& Y (m)")
        self.dir=DIRECTION()
        self.btnStartStop = QtWidgets.QPushButton("START")
        self.btnStartStop.setGeometry(QtCore.QRect(340, 30, 23, 20))
        self.btnStartStop.setDefault(True)
        self.btnPause = QtWidgets.QPushButton("PAUSE")
        self.btnPause.setGeometry(QtCore.QRect(340, 30, 23, 20))
        self.btnPause.setDefault(True)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setBackgroundBrush(QtGui.QColor(103, 113, 121))
        palette = self.scene.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.scene.setPalette(palette)
        self.view.setGeometry(0, 0, 1000, 600) 
        
        mainLayout = QtWidgets.QGridLayout()
        
        oneGroupBox = QtWidgets.QGroupBox("")
        oneGroupBox.setGeometry(0,0,300,300)
        oneLayout = QtWidgets.QGridLayout()
        oneLayout.addWidget(self.stage.GroupBox,0, 0)
        oneLayout.addWidget(self.xcolumn.GroupBox,0, 3)
        oneLayout.addWidget(self.ycolumn.GroupBox,0, 4)
        oneLayout.addWidget(self.dir.GroupBox,0, 1)
        oneLayout.setRowStretch(1, 1)
        oneLayout.setColumnStretch(1, 1)
        oneGroupBox.setLayout(oneLayout)
        
        secGroupBox = QtWidgets.QGroupBox("")
        secGroupBox.setGeometry(0,0,300,300)
        secLayout = QtWidgets.QGridLayout()
        secLayout.addWidget(self.btnStartStop,0, 0)
        secLayout.addWidget(self.btnPause,0, 2)
        secGroupBox.setLayout(secLayout)
        
        mainLayout.addWidget(oneGroupBox,0,0)
        mainLayout.addWidget(self.view,1,0)
        mainLayout.addWidget(secGroupBox,2, 0)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setColumnStretch(0, 1)
        self.cmdGroupBox.setLayout(mainLayout)
        
       
    def createVoltMeterGroupBox(self):
        self.voltMeterGroupBox = QtWidgets.QGroupBox("VoltMeters  [mV]")
        self.voltMeterGroupBox.setGeometry(0,0,100,100)
        
        palette = self.voltMeterGroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
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
        
        self.voltMeterGroupBox.setLayout(mainLayout)
            
        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MYP2()
    widget.resize(2000, 1000)
    widget.show()

    sys.exit(app.exec())