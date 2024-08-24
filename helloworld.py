import sys
import time
from timeloop import Timeloop
from datetime import timedelta
from PySide6.QtCore import SIGNAL
from PySide6 import QtCore, QtWidgets, QtGui# -*- coding: utf-8 -*-
from PySide6.QtGui import QPalette, QColor, QPixmap
from tomo import TOMO1S12V2I
from pickle import NONE


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Tomo 1S 12V 2I')
        
         # Now use a palette to switch to dark colors:
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText,QtGui.QColor(0, 0, 0))
        app.setPalette(palette)
        
        
        
        self.createVoltMeterGroupBox()
        self.createZoneActiveGroupBox()
        self.createCurrentSourceGroupBox()
        self.createSuParamGroupBox()
        self.createControlGroupBox()
        self.createTerminalGroupBox()
        
        pixmap =QtGui.QPixmap('logo.png')
        self.lbllogo = QtWidgets.QLabel() 
        self.lbllogo.setPixmap(pixmap)
        
        self.tl = Timeloop() 
        @self.tl.job(interval=timedelta(seconds=2))
        def sample_job_every_2s(self):
            self.setPeriodicMeasure() 
        
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.currentSourceGroupBox,0, 0)
        mainLayout.addWidget(self.voltMeterGroupBox,1, 0)
        mainLayout.addWidget(self.zoneActiveGroupBox,0, 1)
        mainLayout.addWidget(self.suParamGroupBox,1, 1)
        mainLayout.addWidget(self.controlGroupBox,0, 2)
        mainLayout.addWidget(self.terminalGroupBox,1, 2)
        mainLayout.addWidget(self.lbllogo,2, 2)      
        
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)
        
        self.connect(self.btnConnect, SIGNAL("clicked()"),self.initDut)
        self.connect(self.btnMeas, SIGNAL("clicked()"),self.displayMeas)
        self.connect(self.btnSetSuParam, SIGNAL("clicked()"),self.setSeqU)
        self.connect(self.btnGetSuParam, SIGNAL("clicked()"),self.getSeqU)
        self.connect(self.btnSetival, SIGNAL("clicked()"),self.setIvalSource)
        self.connect(self.btnSetCh, SIGNAL("clicked()"),self.setChannelSource)
        self.connect(self.btnSetZa, SIGNAL("clicked()"),self.setZA)
        self.connect(self.btnCal, SIGNAL("clicked()"),self.setCal)
 
    
    def initDut(self):   
        self.dut = TOMO1S12V2I(comPort=self.inputboxCom.text())
        self.dut.setPwr(pwrIV=1, pwrS=1, pwrS33V=1)
        self.getParam()
        self.displayMeas()
    
    def setPeriodicMeasure(self):
        a = self.checkboxEperiodMeas.checkState()
        if self.checkboxEperiodMeas.checkState() != False:
            self.displayMeas()           
            
    def setEnSeqU(self):
        if self.checkboxEnSeqU.checkState() == True:
            self.dut.su_setMainTask(1)
        else:
            self.dut.su_setMainTask(0)
                        
    def setParam(self): 
        self.setSeqU() 
        self.setZA()
        self.setCurrentSource()
        self.displayMeas()   
        
    def getParam(self):
        self.getSeqU()
        self.getZA()
        self.getCurrentSource()
        
    def setCal(self):
        self.dut.setCal()
        self.displayMeas() 
        
    def setSeqU(self):
        self.dut.setSeqU(I01=self.inputboxSuI01.text(), I02=self.inputboxSuI02.text(), 
                         TuA=self.inputboxSuTuA.text(), TuB=self.inputboxSuTuB.text(), 
                         TuC=self.inputboxSuTuC.text(), TuD=self.inputboxSuTuD.text(),
                         TuE=self.inputboxSuTuE.text(), msTempo =self.inputboxSuTuMs.text() )
    
    def getSeqU(self):
        self.dut.getSeqU()
        self.inputboxSuI01.setText(str(self.dut.SeqU["I01"]))
        self.inputboxSuI02.setText(str(self.dut.SeqU["I02"]))
        self.inputboxSuTuA.setText(str(self.dut.SeqU["TuA"]))
        self.inputboxSuTuB.setText(str(self.dut.SeqU["TuB"]))
        self.inputboxSuTuC.setText(str(self.dut.SeqU["TuC"]))
        self.inputboxSuTuD.setText(str(self.dut.SeqU["TuD"]))
        self.inputboxSuTuE.setText(str(self.dut.SeqU["TuE"]))
        self.inputboxSuTuMs.setText(str(self.dut.SeqU["TempoMs"]))
        
    def setCurrentSource(self):
        self.setIvalSource()
        self.setChannelSource()
        self.setIonSource()        
        
    def getCurrentSource(self):
        self.getIvalSource()
        self.getChannelSource()
        self.getIonSource()
        
    def setIonSource(self):
        if self.checkboxIon.checkState() == False:
            sON= 1
        else :
            sON= 0 
        self.dut.setIon(En=sON)   
        self.displayMeas()       
        
    def getIonSource(self):
        if self.dut.getIon() == 1 :
            self.checkboxIon.setChecked(False)
        else :
            self.checkboxIon.setChecked(True)
         
    def setIvalSource(self):
        Ival = int(self.inputboxIval.text())
        if Ival < 0:
            Ival = Ival * -1
            self.dut.setIpol(Pol=0)
        else:
            self.dut.setIpol(Pol=1)        
        self.dut.setIsource(IuA=Ival)
        self.displayMeas()
           
    def getIvalSource(self):
        Ival = self.dut.getIsource()
        if self.dut.getIpol() == 0:
            Ival = -1 * Ival        
        self.inputboxIval.setText(str(Ival))
        
    def setChannelSource(self):
        self.dut.setSourceChannel(self.inputboxIchanel.text())
        self.displayMeas()
        
    def getChannelSource(self):
        self.inputboxIchanel.setText(str(self.dut.getSourceChannel()))
           
    
    def setZA(self): 
        if self.checkboxZa1.checkState() == False:
            sA1= 0
        else :
            sA1= 1
        if self.checkboxZa2.checkState() == False:
            sA2= 0
        else :
            sA2= 2
        self.dut.setActiveZone(ZA=sA1+sA2) 
        self.displayMeas()   
            
            
    def getZA(self):    
        self.dut.getActiveZone()                  
        if self.dut.ZoneActive["A1"]== 0 :
            self.checkboxZa1.setChecked(False) 
        else:
            self.checkboxZa1.setChecked(True)
        if self.dut.ZoneActive["A2"]== 0 :
            self.checkboxZa2.setChecked(False)            
        else :
            self.checkboxZa2.setChecked(True)
        
            
    def displayMeas(self):
        self.dut.setAcquire()
        self.vm1.display(self.dut.getMeas("V1"))
        self.vm2.display(self.dut.getMeas("V2"))
        self.vm3.display(self.dut.getMeas("V3"))
        self.vm4.display(self.dut.getMeas("V4"))
        self.vm5.display(self.dut.getMeas("V5"))
        self.vm6.display(self.dut.getMeas("V6"))
        self.vm7.display(self.dut.getMeas("V7"))
        self.vm8.display(self.dut.getMeas("V8"))
        self.vm9.display(self.dut.getMeas("V9"))
        self.vm10.display(self.dut.getMeas("V10"))
        self.vm11.display(self.dut.getMeas("V11"))
        self.vm12.display(self.dut.getMeas("V12"))
        self.imZa1.display(1000.0 * self.dut.getMeas("I1"))
        self.imZa2.display(1000.0 * self.dut.getMeas("I2"))
        self.imS.display(1000.0 * self.dut.getMeas("ISOURCE"))
        self.vmS.display(self.dut.getMeas("VSOURCE"))
        R = (float) (self.dut.getMeas("VSOURCE")) / (1000.0 * (float) (self.dut.getMeas("ISOURCE")) )
        if R > 2700000.0 :
            R = 2700000
        if R < 0 : 
            R = 2700000
        self.Rcal.display(R)
        
            
    
    def createTerminalGroupBox(self):
        self.terminalGroupBox = QtWidgets.QGroupBox("Terminal")
        self.terminalGroupBox.setGeometry(0,0,30,100)
        palette = self.terminalGroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.terminalGroupBox.setPalette(palette)
        
        mainLayout = QtWidgets.QGridLayout()  
        
        # cmd line
        self.inputboxCmdLine = QtWidgets.QLineEdit()
        self.inputboxCmdLine.setText("AT=?")  
        
        self.lblCmdLine = QtWidgets.QLabel() 
        self.lblCmdLine.setText("AT CMD")     
        palette = self.lblCmdLine.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblCmdLine.setPalette(palette)
        
        mainLayout.addWidget(self.lblCmdLine,1, 0)
        mainLayout.addWidget(self.inputboxCmdLine,1, 1)
        
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        
        self.controlGroupBox.setLayout(mainLayout)
              
    def createControlGroupBox(self):
        self.controlGroupBox = QtWidgets.QGroupBox("Control")
        self.controlGroupBox.setGeometry(0,0,30,100)
        palette = self.controlGroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.controlGroupBox.setPalette(palette)
        
        mainLayout = QtWidgets.QGridLayout()  
        
        # Com
        self.inputboxCom = QtWidgets.QLineEdit()
        self.inputboxCom.setText("/dev/ttyACM0")  
        
        self.lblSuCom = QtWidgets.QLabel() 
        self.lblSuCom.setText("Com Port")     
        palette = self.lblSuCom.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblSuCom.setPalette(palette)
        
        mainLayout.addWidget(self.lblSuCom,0, 0)
        mainLayout.addWidget(self.inputboxCom,0, 1)
        
        # Init Comport
        self.btnConnect = QtWidgets.QPushButton("INIT")
        self.btnConnect.setDefault(True)
        mainLayout.addWidget(self.btnConnect,1, 1)
        
          # Refresh listcom
        self.btnComList = QtWidgets.QPushButton("List PORT COM")
        self.btnComList.setDefault(True)
        mainLayout.addWidget(self.btnComList,1, 0)
        
        self.btnMeas = QtWidgets.QPushButton("Get MEASURE")
        self.btnMeas.setDefault(True)
        mainLayout.addWidget(self.btnMeas,2, 1)
        
        self.btnCal = QtWidgets.QPushButton("CALIBRATION")
        self.btnCal.setDefault(True)
        mainLayout.addWidget(self.btnCal,2, 0)
        
        
        lblTask = QtWidgets.QLabel()
        mainLayout.addWidget(lblTask,3, 0)
        lblTask.setText("Enable task")
        
        # Periodic Measure
        self.checkboxEperiodMeas = QtWidgets.QCheckBox("Periodic Measure task")
        self.checkboxEperiodMeas.setChecked(False) 
        self.checkboxEperiodMeas.toggled.connect(self.setPeriodicMeasure)
        mainLayout.addWidget(self.checkboxEperiodMeas,4, 0)
         # Seq Unitai Measure
        self.checkboxEnSeqU = QtWidgets.QCheckBox("Sequence Unitaire task")
        self.checkboxEnSeqU.setChecked(False) 
        self.checkboxEnSeqU.toggled.connect(self.setEnSeqU)
        mainLayout.addWidget(self.checkboxEnSeqU,5, 0)
        
        
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        
 
        self.controlGroupBox.setLayout(mainLayout)
           
    def createSuParamGroupBox(self):
        self.suParamGroupBox = QtWidgets.QGroupBox("Sequence Unitaire")
        self.suParamGroupBox.setGeometry(0,0,30,100)
        palette = self.suParamGroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.suParamGroupBox.setPalette(palette)
        
        mainLayout = QtWidgets.QGridLayout()   
        
        # SuI01
        self.inputboxSuI01 = QtWidgets.QLineEdit()
        self.inputboxSuI01.setText("")  
        
        self.lblSuI01 = QtWidgets.QLabel() 
        self.lblSuI01.setText("IO1 (uA)")     
        palette = self.lblSuI01.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblSuI01.setPalette(palette)
        
        mainLayout.addWidget(self.lblSuI01,0, 0)
        mainLayout.addWidget(self.inputboxSuI01,0, 1)
        
         # SuI02
        self.inputboxSuI02 = QtWidgets.QLineEdit()
        self.inputboxSuI02.setText("")  
        
        self.lblSuI02 = QtWidgets.QLabel() 
        self.lblSuI02.setText("IO2 (uA)")     
        palette = self.lblSuI02.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblSuI02.setPalette(palette)
        
        mainLayout.addWidget(self.lblSuI02,1, 0)
        mainLayout.addWidget(self.inputboxSuI02,1, 1)
        
         # SuTuA
        self.inputboxSuTuA = QtWidgets.QLineEdit()
        self.inputboxSuTuA.setText("")  
        
        self.lblSuTuA = QtWidgets.QLabel() 
        self.lblSuTuA.setText("TuA (s)")     
        palette = self.lblSuTuA.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblSuTuA.setPalette(palette)
        
        mainLayout.addWidget(self.lblSuTuA,2, 0)
        mainLayout.addWidget(self.inputboxSuTuA,2, 1)
        
         # SuTuB
        self.inputboxSuTuB = QtWidgets.QLineEdit()
        self.inputboxSuTuB.setText("")  
        
        self.lblSuTuB = QtWidgets.QLabel() 
        self.lblSuTuB.setText("TuB (s)")     
        palette = self.lblSuTuB.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblSuTuB.setPalette(palette)
        
        mainLayout.addWidget(self.lblSuTuB,3, 0)
        mainLayout.addWidget(self.inputboxSuTuB,3, 1)
        
         # SuTuC
        self.inputboxSuTuC = QtWidgets.QLineEdit()
        self.inputboxSuTuC.setText("")  
        
        self.lblSuTuC = QtWidgets.QLabel() 
        self.lblSuTuC.setText("TuC (s)")     
        palette = self.lblSuTuC.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblSuTuC.setPalette(palette)
        
        mainLayout.addWidget(self.lblSuTuC,4, 0)
        mainLayout.addWidget(self.inputboxSuTuC,4, 1)
        
         # SuTuD
        self.inputboxSuTuD = QtWidgets.QLineEdit()
        self.inputboxSuTuD.setText("")  
        
        self.lblSuTuD = QtWidgets.QLabel() 
        self.lblSuTuD.setText("TuD (s)")     
        palette = self.lblSuTuD.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblSuTuD.setPalette(palette)
        
        mainLayout.addWidget(self.lblSuTuD,5, 0)
        mainLayout.addWidget(self.inputboxSuTuD,5, 1)
        
         # SuTuE
        self.inputboxSuTuE = QtWidgets.QLineEdit()
        self.inputboxSuTuE.setText("")  
        
        self.lblSuTuE = QtWidgets.QLabel() 
        self.lblSuTuE.setText("TuE (s)")     
        palette = self.lblSuTuE.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblSuTuE.setPalette(palette)
        
        mainLayout.addWidget(self.lblSuTuE,6, 0)
        mainLayout.addWidget(self.inputboxSuTuE,6, 1)
        
         # SuTuMs
        self.inputboxSuTuMs = QtWidgets.QLineEdit()
        self.inputboxSuTuMs.setText("")  
        
        self.lblSuTuMs = QtWidgets.QLabel() 
        self.lblSuTuMs.setText("TuMs (ms)")     
        palette = self.lblSuTuMs.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))
        self.lblSuTuMs.setPalette(palette)
        
        mainLayout.addWidget(self.lblSuTuMs,7, 0)
        mainLayout.addWidget(self.inputboxSuTuMs,7, 1)
        
        # Set Param button 
        self.btnSetSuParam= QtWidgets.QPushButton("Set")
        self.btnSetSuParam.setDefault(True)
        mainLayout.addWidget(self.btnSetSuParam,8, 1)
        
        # Set Param button 
        self.btnGetSuParam= QtWidgets.QPushButton("Get")
        self.btnGetSuParam.setDefault(True)
        mainLayout.addWidget(self.btnGetSuParam,8, 0)
        
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
 
        self.suParamGroupBox.setLayout(mainLayout)
         
    def createCurrentSourceGroupBox(self):
        self.currentSourceGroupBox = QtWidgets.QGroupBox("Current Source")
        self.currentSourceGroupBox.setGeometry(0,0,30,100)
        palette = self.currentSourceGroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.currentSourceGroupBox.setPalette(palette)
        
        mainLayout = QtWidgets.QGridLayout()   
        
        # ION
        self.checkboxIon = QtWidgets.QCheckBox()
        self.checkboxIon.setChecked(False)  
        self.checkboxIon.toggled.connect(self.setIonSource)
        
        self.lblIon = QtWidgets.QLabel() 
        self.lblIon.setText("R CAL = 1kOhm")     
        palette = self.lblIon.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(31, 160, 85))
        self.lblIon.setPalette(palette)
        
        mainLayout.addWidget(self.lblIon,0, 0)
        mainLayout.addWidget(self.checkboxIon,0, 1)     
        
        
        # Source current
        self.inputboxIval = QtWidgets.QLineEdit()
        self.inputboxIval.setText("0")  
        
        self.lblIval = QtWidgets.QLabel() 
        self.lblIval.setText("Current (uA)")     
        palette = self.lblIval.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(31, 160, 85))
        self.lblIval.setPalette(palette)
        
        # Set Param button 
        self.btnSetival = QtWidgets.QPushButton("Set I")
        self.btnSetival.setDefault(True)
        
        mainLayout.addWidget(self.btnSetival,1, 2)        
        mainLayout.addWidget(self.lblIval,1, 0)
        mainLayout.addWidget(self.inputboxIval,1, 1)
        
        # Source channel
        self.inputboxIchanel = QtWidgets.QLineEdit()
        self.inputboxIchanel.setText("0")  
        
        self.lblIchanel = QtWidgets.QLabel() 
        self.lblIchanel.setText("Source Channel")     
        palette = self.lblIchanel.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(31, 160, 85))
        self.lblIchanel.setPalette(palette)
        
        # Set Param button 
        self.btnSetCh = QtWidgets.QPushButton("Set Channel")
        self.btnSetCh.setDefault(True)
        
        mainLayout.addWidget(self.btnSetCh,2, 2)
        
        mainLayout.addWidget(self.lblIchanel,2, 0)
        mainLayout.addWidget(self.inputboxIchanel,2, 1)
        
        # Isource meas
        self.imS = QtWidgets.QLCDNumber()
        self.imS.setGeometry(0,0,100,100)
        self.imS.setSegmentStyle(self.imS.SegmentStyle.Flat)
        palette = self.imS.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(31, 160, 85)) # foreground color
        palette.setColor(palette.Light, QtGui.QColor(53, 53, 53))  # "light" border # background color
        palette.setColor(palette.Dark, QtGui.QColor(53, 53, 53)) # "dark" border
        self.imS.setPalette(palette)
        self.imS.display(0)
        
        
        self.lblimS = QtWidgets.QLabel() 
        self.lblimS.setText("Isource (uA)")     
        palette = self.lblimS.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(31, 160, 85))
        self.lblimS.setPalette(palette)
        
        mainLayout.addWidget(self.lblimS,3, 0)
        mainLayout.addWidget(self.imS,3, 1)
        
        
        # Vsource meas
        self.vmS = QtWidgets.QLCDNumber()
        self.vmS.setGeometry(0,0,100,100)
        self.vmS.setSegmentStyle(self.vmS.SegmentStyle.Flat)
        palette = self.vmS.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(31, 160, 85)) # foreground color
        palette.setColor(palette.Light, QtGui.QColor(53, 53, 53))  # "light" border # background color
        palette.setColor(palette.Dark, QtGui.QColor(53, 53, 53)) # "dark" border
        self.vmS.setPalette(palette)
        self.vmS.display(0)
        
        
        self.lblvmS = QtWidgets.QLabel() 
        self.lblvmS.setText("Vsource (mV)")     
        palette = self.lblvmS.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(31, 160, 85))
        self.lblvmS.setPalette(palette)
        
        mainLayout.addWidget(self.lblvmS,4, 0)
        mainLayout.addWidget(self.vmS,4, 1)  
        
        
        
        
        self.Rcal = QtWidgets.QLCDNumber()
        self.Rcal.setGeometry(0,0,100,100)
        self.Rcal.setSegmentStyle(self.vmS.SegmentStyle.Flat)
        palette = self.Rcal.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(31, 160, 85)) # foreground color
        palette.setColor(palette.Light, QtGui.QColor(53, 53, 53))  # "light" border # background color
        palette.setColor(palette.Dark, QtGui.QColor(53, 53, 53)) # "dark" border
        self.Rcal.setPalette(palette)
        self.Rcal.display(0)
        
        self.lblRcal = QtWidgets.QLabel() 
        self.lblRcal.setText("Rsource (Ohm)")     
        palette = self.lblRcal.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(31, 160, 85))
        self.lblRcal.setPalette(palette)
        
        mainLayout.addWidget(self.lblRcal,5, 0)
        mainLayout.addWidget(self.Rcal,5, 1)
        
             
              
        
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
 
        self.currentSourceGroupBox.setLayout(mainLayout)
          
    def createZoneActiveGroupBox(self):
        self.zoneActiveGroupBox = QtWidgets.QGroupBox("Zone Active  [uA]")
        self.zoneActiveGroupBox.setGeometry(0,0,30,100)
        palette = self.zoneActiveGroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.zoneActiveGroupBox.setPalette(palette)
        
              
        self.checkboxZa1 = QtWidgets.QCheckBox()
        self.checkboxZa1.setChecked(True)
        self.checkboxZa2 = QtWidgets.QCheckBox()
        self.checkboxZa2.setChecked(False)
        
        
        self.lblza1 = QtWidgets.QLabel()
        self.lblza2 = QtWidgets.QLabel()
        self.lblza1.setText("ZA 1")
        self.lblza2.setText("ZA 2")
        
                # get the palette
        palette = self.lblza1.palette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(223, 109, 20))
        self.lblza1.setPalette(palette)
        self.lblza2.setPalette(palette)

        self.imZa1 = QtWidgets.QLCDNumber()
        self.imZa2 = QtWidgets.QLCDNumber()
        
        self.imZa1.setGeometry(0,0,100,100) 
        self.imZa2.setGeometry(0,0,100,100)
        self.imZa1.setSegmentStyle(self.imZa1.SegmentStyle.Flat)
        self.imZa2.setSegmentStyle(self.imZa2.SegmentStyle.Flat)
     
        # get the palette
        palette = self.imZa1.palette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(223, 109, 20))
        # background color
        palette.setColor(palette.Light, QtGui.QColor(53, 53, 53))  # "light" border
        palette.setColor(palette.Dark, QtGui.QColor(53, 53, 53)) # "dark" border
        
        self.imZa1.setPalette(palette)
        self.imZa2.setPalette(palette)
 
        self.imZa1.display(0)
        self.imZa2.display(0)
        
        # Set Param button 
        self.btnSetZa = QtWidgets.QPushButton("Set ZA")
        self.btnSetZa.setDefault(True)

        mainLayout = QtWidgets.QGridLayout()        
        mainLayout.addWidget(self.lblza1,0, 0)
        mainLayout.addWidget(self.lblza2,1, 0)

        mainLayout.addWidget(self.imZa1,0, 1)
        mainLayout.addWidget(self.imZa2,1, 1)
        
        mainLayout.addWidget(self.checkboxZa1,0, 2)
        mainLayout.addWidget(self.checkboxZa2,1, 2)
        mainLayout.addWidget(self.btnSetZa,2, 0)
        
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
 
        self.zoneActiveGroupBox.setLayout(mainLayout)
            
    def createVoltMeterGroupBox(self):
        self.voltMeterGroupBox = QtWidgets.QGroupBox("VoltMeters  [mV]")
        self.voltMeterGroupBox.setGeometry(0,0,100,100)
        
        palette = self.voltMeterGroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.voltMeterGroupBox.setPalette(palette)
        
        self.lblvm1 = QtWidgets.QLabel()
        self.lblvm2 = QtWidgets.QLabel()
        self.lblvm3 = QtWidgets.QLabel()
        self.lblvm4 = QtWidgets.QLabel()
        self.lblvm5 = QtWidgets.QLabel()
        self.lblvm6 = QtWidgets.QLabel()
        self.lblvm7 = QtWidgets.QLabel()
        self.lblvm8 = QtWidgets.QLabel()
        self.lblvm9 = QtWidgets.QLabel()
        self.lblvm10 = QtWidgets.QLabel()
        self.lblvm11 = QtWidgets.QLabel()
        self.lblvm12 = QtWidgets.QLabel()
        
        self.lblvm1.setText("Channel 1")
        self.lblvm2.setText("Channel 2")
        self.lblvm3.setText("Channel 3")
        self.lblvm4.setText("Channel 4")
        self.lblvm5.setText("Channel 5")
        self.lblvm6.setText("Channel 6")
        self.lblvm7.setText("Channel 7")
        self.lblvm8.setText("Channel 8")
        self.lblvm9.setText("Channel 9")
        self.lblvm10.setText("Channel 10")
        self.lblvm11.setText("Channel 11")
        self.lblvm12.setText("Channel 12")
        
        # get the palette
        palette = self.lblvm1.palette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(49, 140, 231))
        self.lblvm1.setPalette(palette)
        self.lblvm2.setPalette(palette)
        self.lblvm3.setPalette(palette)
        self.lblvm4.setPalette(palette)
        self.lblvm5.setPalette(palette)
        self.lblvm6.setPalette(palette)
        self.lblvm7.setPalette(palette)
        self.lblvm8.setPalette(palette)
        self.lblvm9.setPalette(palette)
        self.lblvm10.setPalette(palette)
        self.lblvm11.setPalette(palette)
        self.lblvm12.setPalette(palette)
        
        
        
        self.vm1 = QtWidgets.QLCDNumber()
        self.vm2 = QtWidgets.QLCDNumber()
        self.vm3 = QtWidgets.QLCDNumber()
        self.vm4 = QtWidgets.QLCDNumber()
        self.vm5 = QtWidgets.QLCDNumber()
        self.vm6 = QtWidgets.QLCDNumber()
        self.vm7 = QtWidgets.QLCDNumber()
        self.vm8 = QtWidgets.QLCDNumber()
        self.vm9 = QtWidgets.QLCDNumber()
        self.vm10 = QtWidgets.QLCDNumber()
        self.vm11 = QtWidgets.QLCDNumber()
        self.vm12 = QtWidgets.QLCDNumber()
        
        self.vm1.setGeometry(0,0,100,100) 
        self.vm2.setGeometry(0,0,100,100)
        self.vm3.setGeometry(0,0,100,100)
        self.vm4.setGeometry(0,0,100,100)
        self.vm5.setGeometry(0,0,100,100)
        self.vm6.setGeometry(0,0,100,100)
        self.vm7.setGeometry(0,0,100,100)
        self.vm8.setGeometry(0,0,100,100)
        self.vm9.setGeometry(0,0,100,100)
        self.vm10.setGeometry(0,0,100,100)
        self.vm11.setGeometry(0,0,100,100)
        self.vm12.setGeometry(0,0,100,100)

        self.vm1.setSegmentStyle(self.vm1.SegmentStyle.Flat)
        self.vm2.setSegmentStyle(self.vm2.SegmentStyle.Flat)
        self.vm3.setSegmentStyle(self.vm3.SegmentStyle.Flat)
        self.vm4.setSegmentStyle(self.vm4.SegmentStyle.Flat)
        self.vm5.setSegmentStyle(self.vm5.SegmentStyle.Flat)
        self.vm6.setSegmentStyle(self.vm6.SegmentStyle.Flat)
        self.vm7.setSegmentStyle(self.vm7.SegmentStyle.Flat)
        self.vm8.setSegmentStyle(self.vm8.SegmentStyle.Flat)
        self.vm9.setSegmentStyle(self.vm9.SegmentStyle.Flat)
        self.vm10.setSegmentStyle(self.vm10.SegmentStyle.Flat)
        self.vm11.setSegmentStyle(self.vm11.SegmentStyle.Flat)
        self.vm12.setSegmentStyle(self.vm12.SegmentStyle.Flat)
        
        # get the palette
        palette = self.vm1.palette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(49, 140, 231))
        # background color
        palette.setColor(palette.Light, QtGui.QColor(53, 53, 53))  # "light" border
        palette.setColor(palette.Dark, QtGui.QColor(53, 53, 53)) # "dark" border
        
        self.vm1.setPalette(palette)
        self.vm2.setPalette(palette)
        self.vm3.setPalette(palette)
        self.vm4.setPalette(palette)
        self.vm5.setPalette(palette)
        self.vm6.setPalette(palette)
        self.vm7.setPalette(palette)
        self.vm8.setPalette(palette)
        self.vm9.setPalette(palette)
        self.vm10.setPalette(palette)
        self.vm11.setPalette(palette)
        self.vm12.setPalette(palette)
        
        self.vm1.display(0)
        self.vm2.display(0)
        self.vm3.display(0)
        self.vm4.display(0)
        self.vm5.display(0)
        self.vm6.display(0)
        self.vm7.display(0)
        self.vm8.display(0)
        self.vm9.display(0)
        self.vm10.display(0)
        self.vm11.display(0)
        self.vm12.display(0)
        
        mainLayout = QtWidgets.QGridLayout()
        
        mainLayout.addWidget(self.lblvm1,0, 0)
        mainLayout.addWidget(self.lblvm2,1, 0)
        mainLayout.addWidget(self.lblvm3,2, 0)
        mainLayout.addWidget(self.lblvm4,3, 0)
        mainLayout.addWidget(self.lblvm5,4, 0)
        mainLayout.addWidget(self.lblvm6,5, 0)
        mainLayout.addWidget(self.lblvm7,6, 0)
        mainLayout.addWidget(self.lblvm8,7, 0)
        mainLayout.addWidget(self.lblvm9,8, 0)
        mainLayout.addWidget(self.lblvm10,9, 0)
        mainLayout.addWidget(self.lblvm11,10, 0)
        mainLayout.addWidget(self.lblvm12,12, 0)
        
        mainLayout.addWidget(self.vm1,0, 1)
        mainLayout.addWidget(self.vm2,1, 1)
        mainLayout.addWidget(self.vm3,2, 1)
        mainLayout.addWidget(self.vm4,3, 1)
        mainLayout.addWidget(self.vm5,4, 1)
        mainLayout.addWidget(self.vm6,5, 1)
        mainLayout.addWidget(self.vm7,6, 1)
        mainLayout.addWidget(self.vm8,7, 1)
        mainLayout.addWidget(self.vm9,8, 1)
        mainLayout.addWidget(self.vm10,9, 1)
        mainLayout.addWidget(self.vm11,10, 1)
        mainLayout.addWidget(self.vm12,12, 1)
        
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
 
        self.voltMeterGroupBox.setLayout(mainLayout)
            
        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(1000, 600)
    widget.show()

    sys.exit(app.exec())