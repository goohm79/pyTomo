import sys
import time
import os.path
import threading
from datetime import datetime

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
        
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.runtimerPlotrefresh)
        self.countTimer = 0
        
        self.timerXPS = QTimer()
        self.timerXPS.setInterval(100)
        self.timerXPS.timeout.connect(self.runtimerXPS)
        
        self.initPiloteGui()
        

        
    def closeEvent(self, event):        
        self.Ilim = self.powerSupply.getI()
        self.Vlim = self.powerSupply.getV()
        self.StatePS = self.powerSupply.getonOff()
        self.saveJsonConf()
        self.stopThreadReadLine()
        self.shutdown()
    
        
    def startThreadReadLine(self):  
        if self.initState == 1:
            try:
                # création de thread
                self.t1 = threading.Thread(target=self.runThreadReadLine)
                self.t1State=1
                self.t1.start()                
                
            except:
                self.t1State=0
        
    def stopThreadReadLine(self):
        try: 
            self.timer.stop()
            self.timerXPS.stop()
            try:
                self.logFileName.close()  
            except:
                None
            self.t1State=0
            self.t1.join()
        except:
            NONE
               
    def runThreadReadLine(self): 
        MN1 = 60
        MN2 =120
        MN10 = 600
        H1 = 3600
        H24 = H1 *24
        SamplePeriod = 0.1
        self.countAcquisition = 0
        self.enAcquisition = 0
        self.depolStateOld = self.depolState 
        while(self.t1State==1):
                try:             
                    self.ExtStrLine = (str)(self.dut.rLineCom())
                    if len(self.ExtStrLine) !=0:
                        if self.ExtStrLine !="OK\r\n":
                            self.t1 = time.time()
                            self.tlog = datetime.now()
                            self.enAcquisition = 0
                            self.extractExtStrLine(valStr = self.ExtStrLine)
                            self.countAcquisition = self.countAcquisition + SamplePeriod
# puis, échantillonnage de 1 mn pendant 1 heure
# puis échantillonnage de 10 mn pendant 24h
# puis échantillonnage de 1h le reste du temps. 
                            if self.startLogSate == 1 :
                                if self.t1 < (self.tpol + MN2):
                                    # au moment de la transition : échantillonnage de 0.1 s pendant 2 mn
                                    self.enAcquisition = 1
                                    self.t2 = self.t1
                                    if self.depolState == self.depolStateOld:   #filtre sur tension à la commuttation du relai                   
                                        if self.idx > self.idxFirst:
                                            self.idxPol = self.idx - self.idxFirst 
                                        else:
                                            self.idxPol = 65534 - self.idxFirst +  self.idx
                                    else:
                                        self.idxFirst = self.idx
                                        self.idxPol = 0
                                        self.depolStateOld = self.depolState
                                    self.timeS = 0.1 * self.idxPol
                                else:
                                    if self.t1 >= self.t2 :
                                        self.enAcquisition = 1
                                        if self.t1 >= self.tpol + H24 :
                                        # puis échantillonnage de 1h le reste du temps. 
                                            self.t2 = self.t1 + H1
                                            self.timeS = self.timeS + H1
                                        elif self.t1 >=  self.tpol + H1 :
                                        # puis échantillonnage de 10 mn pendant 24h
                                            self.t2 = self.t1 + MN10
                                            self.timeS = self.timeS + MN10
                                        else :
                                        # puis, échantillonnage de 1 mn pendant 1 heure
                                            self.t2 = self.t1 + MN1 
                                            self.timeS = self.timeS + MN1                              
                                if self.enAcquisition == 1: # and self.idxPol != 2:  
                                    self.guiMeasTabToLogFile()
                                    self.enAcquisition = 0 
                        else:
                            None
                            self.dut.flushCom() 
                except:
                    None
                    self.dut.flushCom()   
             
    def guiMeasTabToLogFile(self):
        try:
            fileStr = str(self.timeS) + ";" +  str(self.tlog)+ ";" + str(self.depolState)+ ";"  \
                                                + str("{0:.3f}".format(self.guiMeas["VPS"]))+ ";" \
                                                + str("{0:.3f}".format(self.guiMeas["IPS"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["V1"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["V2"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["V3"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["V4"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["V5"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["V6"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["I1"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["I2"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["I3"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["I4"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["I5"]))+ ";" \
                                                + str("{0:.1f}".format(self.guiMeas["I6"]))+ "\r"                                  
            self.ExtractLogFile = open(self.logFileName, "a")
            self.ExtractLogFile.writelines(fileStr)
            self.ExtractLogFile.close()                                 
        except:
            try:
                self.ExtractLogFile.close() 
            except:
                NONE 
            
    def measXPS(self): 
        self.guiMeas["IPS"] = self.powerSupply.measI()
        self.guiMeas["VPS"] = self.powerSupply.measV() 

     
             
    def runtimerPlotrefresh(self):
        self.appendChrono() 
        self.updateLCD()              
        if self.powerSupply.getonOff() == 1:
            self.powerSupply.displayVm(v=self.guiMeas["VPS"]) 
            self.powerSupply.displayIm(i=self.guiMeas["IPS"])  
        else:
            self.powerSupply.displayVm(v=0) 
            self.powerSupply.displayIm(i=0) 
        self.countTimer = self.countTimer +1
        if self.countTimer == 2:
            self.saveJsonConf() 
            self.countTimer =  0       
    
    def runtimerXPS(self):
        try:
            self.measXPS()
        except:
            None
            
    def appendChrono(self):
        try:
            self.time = self.time[1:]
            self.time.append(self.countAcquisition)
            
            self.tabmV1 = self.tabmV1[1:]
            self.tabmV1.append(self.guiMeas["V1"])
            self.linemV1.setData(x=self.time, y=self.tabmV1)
            
            self.tabmV2 = self.tabmV2[1:]
            self.tabmV2.append(self.guiMeas["V2"])
            self.linemV2.setData(self.time, self.tabmV2)
            
            self.tabmV3 = self.tabmV3[1:]
            self.tabmV3.append(self.guiMeas["V3"])
            self.linemV3.setData(self.time, self.tabmV3)
            
            self.tabmV4 = self.tabmV4[1:]
            self.tabmV4.append(self.guiMeas["V4"])
            self.linemV4.setData(self.time, self.tabmV4)
            
            self.tabmV5 = self.tabmV5[1:]
            self.tabmV5.append(self.guiMeas["V5"])
            self.linemV5.setData(self.time, self.tabmV5)
            
            self.tabmV6 = self.tabmV6[1:]
            self.tabmV6.append(self.guiMeas["V6"])
            self.linemV6.setData(self.time, self.tabmV6)
            
            
            self.tabmI1 = self.tabmI1[1:]
            self.tabmI1.append(self.guiMeas["I1"])
            self.linemI1.setData(self.time, self.tabmI1)
            
            self.tabmI2 = self.tabmI2[1:]
            self.tabmI2.append(self.guiMeas["I2"])
            self.linemI2.setData(self.time, self.tabmI2)
            
            self.tabmI3 = self.tabmI3[1:]
            self.tabmI3.append(self.guiMeas["I3"])
            self.linemI3.setData(self.time, self.tabmI3)
            
            self.tabmI4 = self.tabmI4[1:]
            self.tabmI4.append(self.guiMeas["I4"])
            self.linemI4.setData(self.time, self.tabmI4)
            
            self.tabmI5 = self.tabmI5[1:]
            self.tabmI5.append(self.guiMeas["I5"])
            self.linemI5.setData(self.time, self.tabmI5)
            
            self.tabmI6 = self.tabmI6[1:]
            self.tabmI6.append(self.guiMeas["I6"])
            self.linemI6.setData(self.time, self.tabmI6)
        except:
            NONE     
               
    def extractExtStrLine(self, valStr = ""): 
        #print(str(valStr))
        try:
            tabStrVal = valStr.split(';', 12)    
            idx = 0  
            self.idx = float(tabStrVal[idx]) 
            self.guiMeas["V1"]=self.calV(x=float(tabStrVal[idx+1]))
            self.guiMeas["V2"]=self.calV(x=float(tabStrVal[idx+2]))
            self.guiMeas["V3"]=self.calV(x=float(tabStrVal[idx+3]))
            self.guiMeas["V4"]=self.calV(x=float(tabStrVal[idx+4]))
            self.guiMeas["V5"]=self.calV(x=float(tabStrVal[idx+5]))
            self.guiMeas["V6"]=self.calV(x=float(tabStrVal[idx+6]))
            self.guiMeas["I1"]=self.calI(x=float(tabStrVal[idx+7]))
            self.guiMeas["I2"]=self.calI(x=float(tabStrVal[idx+8]))
            self.guiMeas["I3"]=self.calI(x=float(tabStrVal[idx+9]))
            self.guiMeas["I4"]=self.calI(x=float(tabStrVal[idx+10]))
            self.guiMeas["I5"]=self.calI(x=float(tabStrVal[idx+11]))
            self.guiMeas["I6"]=self.calI(x=float(tabStrVal[idx+12]))
            
            
        except:
            NONE
    
    def calV(self, x=0):
        if x < -25:
            z = -1 * x / 1000
            y = -1000*((0.154 * (z**4)) -  (0.373 * (z**3)) + (0.352 * (z**2)) + (0.905 * (z)))          
        else:
            y = x
        return y
    
    def calI(self, x=0):
        if x > 100:
            y = (5.85037286e-11 * (x**4)) -  (1.5054609175e-7 * (x**3)) + (0.000163975 * (x**2)) + (0.963615 * (x))
        else:
            y = x
        return y
    
    def updateLCD(self):
        self.vm1.lcd.display(self.guiMeas["V1"])
        self.vm2.lcd.display(self.guiMeas["V2"])
        self.vm3.lcd.display(self.guiMeas["V3"])
        self.vm4.lcd.display(self.guiMeas["V4"])
        self.vm5.lcd.display(self.guiMeas["V5"])
        self.vm6.lcd.display(self.guiMeas["V6"])
        self.am1.lcd.display(self.guiMeas["I1"])
        self.am2.lcd.display(self.guiMeas["I2"])
        self.am3.lcd.display(self.guiMeas["I3"])
        self.am4.lcd.display(self.guiMeas["I4"])
        self.am5.lcd.display(self.guiMeas["I5"])
        self.am6.lcd.display(self.guiMeas["I6"])     
    
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
        self.timerXPS.stop()
        self.logDateTime = datetime.now()
        self.logFileName = "log_p2Pilote_" + "_date-" + str(self.logDateTime)
        file  = QtWidgets.QFileDialog.getSaveFileName(None, "Save a file csv", self.logFileName + ".csv",             "*.csv")
        self.logFileName = file[0]
        self.jsonConf.SetJsonParam(name="CSVfilePath",val=self.logFileName)
        self.ExtractLogFileName = file[0]
        if not os.path.exists(self.ExtractLogFileName):
            self.ExtractLogFile = open(self.ExtractLogFileName, "w")
            self.strLine = "timeSeconde,time;polarState;VPS(V);IPS(A);V1(mV);V2(mV);V3(mV);V4(mV);V5(mV);V6(mV);I1(mA);I2(mA);I3(mA);I4(mA);I5(mA);I6(mA)\r"
            self.ExtractLogFile.writelines(self.strLine)
            self.ExtractLogFile.close()
        self.timerXPS.start()
        
    def startStopLog(self):
        self.timerXPS.stop()
        self.tpol = time.time() 
        if self.startLogSate == 0: # start log et acuquiition
            self.btnStartStop.setText("STOP LOG")
            pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
            self.btnStartStop.setPalette(pal)            
            self.startLogSate = 1
            
        else: # stop
            self.btnStartStop.setText("START LOG")
            pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
            self.btnStartStop.setPalette(pal)
            self.startLogSate = 0
            #self.dut.stopP2Pilote()
        self.timerXPS.start()
        
        
    def polDepol(self):   
        self.timerXPS.stop()
        self.tpol = time.time()  
        self.idxPol = 0
        if self.depolState == 0: # polarisattion state
            self.btnPoldePol.setText("SET DEPOL")
            pal.setColor(QPalette.ButtonText, QColor(231, 140, 49))
            self.btnPoldePol.setPalette(pal)  
            self.powerSupply.SetonOff(state=1)  
            self.dut.setPolP2Pilot()
            self.depolState = 1 
            self.lblStatePol.setText("PILOTE STATE: POLARISATION")
            pal.setColor(QPalette.WindowText, QColor(49, 140, 231)) 
            self.lblStatePol.setPalette(pal) 
        else: # polarisattion state
            self.btnPoldePol.setText("SET POL")
            pal.setColor(QPalette.ButtonText, QColor(49, 140, 231))
            self.btnPoldePol.setPalette(pal) 
            self.dut.resetPolP2Pilot()
            self.powerSupply.SetonOff(state=0) 
            self.depolState = 0 
            #self.powerSupply.displayVm(v=0) 
            #self.powerSupply.displayIm(i=0) 
            self.lblStatePol.setText("PILOTE STATE: DéPOLARISATION")
            pal.setColor(QPalette.WindowText, QColor(231, 140, 49))
            self.lblStatePol.setPalette(pal) 
        self.timerXPS.start()
              
        
    def setP2Prog(self):
        if self.P2State  == 1:
            self.P2State = 0
            self.textEditTerminal.append("Stop P2 Program")
            self.textEditTerminal.append("Start TOMO Program")
            self.btnEnSeqU.setText("Enable P2 Pilote Prg.")
            self.dut.setP2toTomo()
        else:
            self.P2State = 1
            self.textEditTerminal.append("Stop TOMO Program")
            self.textEditTerminal.append("Start P2Pilote Program")
            self.btnEnSeqU.setText("Enable Tomo Prg.")
            self.dut.setTomotoP2Pilote()
        time.sleep(2)
        del(self.dut)
        del(self.dut)
        self.initState = 0 
        self.t1State = 0
        self.initDut()  
        
            
       
    def setCal(self):
        self.dut.stopP2Pilote()
        self.textEditTerminal.append("Set calibration")
        self.dut.setCal()
        self.displayMeas()
        self.dut.startP2Pilote()
            
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
        self.guiMeas ={}
        self.loadJsonConf()
        self.initState = 0  
        self.t1State = 0 
        self.initDut()
        self.countAcquisition = 0
        self.tpol = time.time() 
        if self.startLogSate == 1: # polarisattion state
            self.btnStartStop.setText("STOP LOG")
            pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
            self.btnStartStop.setPalette(pal)          
        else: # polarisattion state
            self.btnStartStop.setText("START LOG")
            pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
            self.btnStartStop.setPalette(pal)
            
        if self.depolState == 1: # polarisation state
            self.btnPoldePol.setText("SET DEPOL")
            pal.setColor(QPalette.ButtonText, QColor(231, 140, 49))
            self.btnPoldePol.setPalette(pal)  
            self.powerSupply.SetonOff(state=1)   
            self.lblStatePol.setText("PILOTE STATE: POLARISATION")
            pal.setColor(QPalette.WindowText, QColor(49, 140, 231)) 
            self.lblStatePol.setPalette(pal)        
        else: # polarisattion state
            self.btnPoldePol.setText("SET POL")
            pal.setColor(QPalette.ButtonText, QColor(49, 140, 231))
            self.btnPoldePol.setPalette(pal)
            self.powerSupply.SetonOff(state=0)
            self.lblStatePol.setText("PILOTE STATE: DéPOLARISATION")
            pal.setColor(QPalette.WindowText, QColor(231, 140, 49))
            self.lblStatePol.setPalette(pal) 

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
                try:   
                    self.dut.stopP2Pilote()       
                    self.displayMeas()
                    if self.dut.getP2() == 2:
                        self.btnEnSeqU.setText("Enable TOMO Prg.")
                        self.P2State  = 1
                    else:
                        self.P2State  = 0
                        self.btnEnSeqU.setText("Enable P2 Pilote Prg.")
                    pal.setColor(QPalette.WindowText, QColor(0, 255, 0))
                    self.ledTomo.setPalette(pal) 
                except:
                    None                   
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
                self.dut.startP2Pilote()    
                self.btnConnect.setText("Disconnect")
                pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
                self.btnConnect.setPalette(pal) 
                self.timer.start() 
                self.timerXPS.start()
                self.startThreadReadLine()
        else:
            if self.t1State == 1:
                try:
                    self.timer.stop() 
                    self.timerXPS.stop()
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
            self.guiMeas["V1"]=self.dut.getMeas("V1")
            self.guiMeas["V2"]=self.dut.getMeas("V2")
            self.guiMeas["V3"]=self.dut.getMeas("V3")
            self.guiMeas["V4"]=self.dut.getMeas("V4")
            self.guiMeas["V5"]=self.dut.getMeas("V5")
            self.guiMeas["V6"]=self.dut.getMeas("V6")
            self.guiMeas["I1"]=self.dut.getMeas("I1")
            self.guiMeas["I2"]=self.dut.getMeas("I2")
            self.guiMeas["I3"]=self.dut.getMeas("I3")
            self.guiMeas["I4"]=self.dut.getMeas("I4")
            self.guiMeas["I5"]=self.dut.getMeas("I5")
            self.guiMeas["I6"]=self.dut.getMeas("I6")
            self.updateLCD()
            self.powerSupply.displayMeas()
            
     
    
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
        
        self.lblStatePol= QtWidgets.QLabel("PILOTE STATE: DéPOLARISATION")
        pal.setColor(QPalette.WindowText, QColor(231, 140, 49))
        self.lblStatePol.setPalette(pal)
        mainLayout.addWidget(self.lblStatePol,0,3)
        
        self.btnPoldePol = QtWidgets.QPushButton("SET POL")
        pal.setColor(QPalette.ButtonText, QColor(49, 140, 231))
        self.btnPoldePol.setPalette(pal)
        self.btnPoldePol.setDefault(True)
        mainLayout.addWidget(self.btnPoldePol,0,4)
      
        self.plotRange = 500
        self.plotmV = pg.PlotWidget()
        self.plotmV.setBackground((53, 53, 53))
        
        styles = {"color": "grey", "font-size": "18px"}
        self.plotmV.setLabel("left", "Voltage [mV]", **styles)
        #self.plotmV.setLabel("bottom", "Time [sec]", **styles)
        self.plotmV.addLegend()
        self.plotmV.showGrid(x=True, y=True)
        self.plotmV.setYRange(-3000, 3000)
        self.time = []
        self.clearTabmList(tab=self.time)
        pen = pg.mkPen(color=(255, 0, 0))
        self.tabmV1 = []
        self.clearTabmList(tab=self.tabmV1)
        self.linemV1 = self.plotmV.plot(
            self.time,
            self.tabmV1,
            name="V1",
            pen=pen,
            symbol="o",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(0, 255, 0))
        self.tabmV2 = []
        self.clearTabmList(tab=self.tabmV2)
        self.linemV2 = self.plotmV.plot(
            self.time,
            self.tabmV2,
            name="V2",
            pen=pen,
            symbol="t",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(0, 0, 255))
        self.tabmV3 = []
        self.clearTabmList(tab=self.tabmV3)
        self.linemV3 = self.plotmV.plot(
            self.time,
            self.tabmV3,
            name="V3",
            pen=pen,
            symbol="t1",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(255, 0, 255))
        self.tabmV4 = []
        self.clearTabmList(tab=self.tabmV4)
        self.linemV4 = self.plotmV.plot(
            self.time,
            self.tabmV4,
            name="V4",
            pen=pen,
            symbol="t2",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(255, 255, 255))
        self.tabmV5 = []
        self.clearTabmList(tab=self.tabmV5)
        self.linemV5 = self.plotmV.plot(
            self.time,
            self.tabmV5,
            name="V5",
            pen=pen,
            symbol="t3",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(250, 237, 39))
        self.tabmV6 = []
        self.clearTabmList(tab=self.tabmV6)
        self.linemV6 = self.plotmV.plot(
            self.time,
            self.tabmV6,
            name="V6",
            pen=pen,
            symbol="s",
            symbolSize=1,
            symbolBrush="g",
        )
        
        self.plotmA = pg.PlotWidget()
        self.plotmA.setBackground((53, 53, 53))
        pen = pg.mkPen(color=(255, 0, 0))
        styles = {"color": "grey", "font-size": "18px"}
        self.plotmA.setLabel("left", "Current [mA]", **styles)
        self.plotmA.setLabel("bottom", "Time [sec]", **styles)
        self.plotmA.addLegend()
        self.plotmA.showGrid(x=True, y=True)
        self.plotmA.setYRange(0, 3000)
        
        pen = pg.mkPen(color=(255, 0, 0))
        self.tabmI1 = []
        self.clearTabmList(tab=self.tabmI1)
        self.linemI1 = self.plotmA.plot(
            self.time,
            self.tabmI1,
            name="I1",
            pen=pen,
            symbol="o",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(0, 255, 0))
        self.tabmI2 = []
        self.clearTabmList(tab=self.tabmI2)
        self.linemI2 = self.plotmA.plot(
            self.time,
            self.tabmI2,
            name="I2",
            pen=pen,
            symbol="t",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(0, 0, 255))
        self.tabmI3 = []
        self.clearTabmList(tab=self.tabmI3)
        self.linemI3 = self.plotmA.plot(
            self.time,
            self.tabmI3,
            name="I3",
            pen=pen,
            symbol="t1",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(255, 0, 255))
        self.tabmI4 = []
        self.clearTabmList(tab=self.tabmI4)
        self.linemI4 = self.plotmA.plot(
            self.time,
            self.tabmI4,
            name="I4",
            pen=pen,
            symbol="t2",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(255, 255, 255))
        self.tabmI5 = []
        self.clearTabmList(tab=self.tabmI5)
        self.linemI5 = self.plotmA.plot(
            self.time,
            self.tabmI5,
            name="I5",
            pen=pen,
            symbol="t3",
            symbolSize=1,
            symbolBrush="g",
        )
        pen = pg.mkPen(color=(250, 237, 39))
        self.tabmI6 = []
        self.clearTabmList(tab=self.tabmI6)
        self.linemI6 = self.plotmA.plot(
            self.time,
            self.tabmI6,
            name="I6",
            pen=pen,
            symbol="s",
            symbolSize=0.2,
            symbolBrush="g",
        )        
        
      
        mainLayout.addWidget(self.plotmV,1,0,1,5)
        mainLayout.addWidget(self.plotmA,2,0,1,5)
        self.linemI6.clear()
       
        mainLayout.setRowStretch(0,2)
        mainLayout.setColumnStretch(3, 3)
        self.P2PiloteGroupBox.setLayout(mainLayout)      
        
    def clearTabmList (self, tab = []):
        for i in range(self.plotRange):
            tab.append(0)

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
    