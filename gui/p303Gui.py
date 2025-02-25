import sys
import time
import os.path
import threading
import datetime

from ate.tomo import TOMO1S12V2I
from ate.PL303P import PL303
from gui.toolsGui import SDIGIT, PMLINE, Worker

from pickle import NONE
from PySide6.QtCore import SIGNAL, QObject, QTimer
from PySide6 import  QtWidgets, QtGui # -*- coding: utf-8 -*-
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget, QMainWindow, QMessageBox, QGridLayout
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

 
class PL303GUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PL303GUI.py')
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(60, 60, 60))
        pal.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))  
        pal.setColor(QPalette.Button, QColor(60, 60, 60))
        pal.setColor(QPalette.Text, QColor(255, 255, 255))
               
        self.createPL303GroupBox()
        
        self.ps = PL303(comPort="/dev/PL303_COM")
        
        self.setCom()
        self.onOffLock = 1
        self.onOffState = 0
        self.ps.Output(self.onOffState) 

               
        self.mainLayout = QtWidgets.QGridLayout(self)
        self.mainLayout.addWidget(self.PL303GroupBox,0, 1)
        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setColumnStretch(1, 1)
        
        self.connect(self.btnOnOff, SIGNAL("clicked()"),self.onOfflock)
        self.connect(self.btnSet, SIGNAL("clicked()"),self.set)
        
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayMeas)
        self.timer.start() 

        
    def __del__(self):
        NONE
    
    def setCom(self): 
        return self.ps.SetCom()
        
        
    def onOfflock(self):  
        if self.onOffLock == 0:
            self.onOff()
            self.onOffLock = 1 
        else:
            if self.showDialog() == QMessageBox.Ok :
                self.onOffLock =0 
                
    def onOff(self):  
        if self.onOffState == 0:
            self.onOffState = 1
            self.btnOnOff.setText("OFF")
            pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
            self.btnOnOff.setPalette(pal)
        else:
            self.onOffState = 0
            self.btnOnOff.setText("ON")
            pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
            self.btnOnOff.setPalette(pal)
        self.ps.Output(self.onOffState)   
        
    def SetonOff(self, state = 0): 
        self.onOffState = state 
        self.ps.Output(self.onOffState) 
        if self.onOffState == 1:
            self.btnOnOff.setText("OFF")
            pal.setColor(QPalette.ButtonText, QColor(255, 0, 0))
            self.btnOnOff.setPalette(pal)
        else:
            self.btnOnOff.setText("ON")
            pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
            self.btnOnOff.setPalette(pal)
            
    def getonOff(self):
        return self.onOffState
    
    def setVI(self, v=0, i=0):  
        self.v.setVal(v)
        self.i.setVal(i)
        self.ps.Set(fct='V', val=self.v.getVal())
        self.ps.Set(fct='I', val=self.i.getVal())   
        
    def getV(self):  
        return self.v.getVal()
    
    def getI(self):  
        return self.i.getVal()   
           
    def set(self):  
        self.ps.Set(fct='V', val=self.v.getVal())
        self.ps.Set(fct='I', val=self.i.getVal())   
    
    def measV(self):  
        return  self.ps.Meas("V")       
    
    def measI(self): 
        return self.ps.Meas("I")
        
    def displayMeas(self):        
        self.vm.lcd.display(self.measV())
        self.im.lcd.display(self.measI())
        
    def createPL303GroupBox(self):
        self.PL303GroupBox = QtWidgets.QGroupBox("Power Supply [PL303-P]")
        self.PL303GroupBox.setGeometry(0,0,100,50)
        
        palette = self.PL303GroupBox.palette()
        palette.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))     
        self.PL303GroupBox.setPalette(palette)

        self.vm = SDIGIT("Voltage [V]")
        self.im = SDIGIT("Current [A]")
        
        self.v =PMLINE(delta =0.1)
        self.i =PMLINE(delta =0.1)
        
        self.btnOnOff = QtWidgets.QPushButton("ON")
        self.btnOnOff.setDefault(True)
        pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
        self.btnOnOff.setPalette(pal)
        
        self.btnSet = QtWidgets.QPushButton("SET")
        self.btnSet.setDefault(True)
        pal.setColor(QPalette.ButtonText, QColor(0, 255, 0))
        self.btnSet.setPalette(pal)

        mainLayout = QtWidgets.QGridLayout()
        
        mainLayout.addWidget(self.vm.GroupBox,0, 0)
        mainLayout.addWidget(self.im.GroupBox,0, 1)
        mainLayout.addWidget(self.v.GroupBox,1, 0)
        mainLayout.addWidget(self.i.GroupBox,1, 1)
        mainLayout.addWidget(self.btnOnOff,2, 0)
        mainLayout.addWidget(self.btnSet,2, 1)
        
        mainLayout.setRowStretch(0,0)
        self.PL303GroupBox.setLayout(mainLayout)
    
    def showDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Click OK to unlock PL303 !")
        msgBox.setWindowTitle("Click OK to unlock PL303 !")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  
        return msgBox.exec()

    
       
if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = PL303GUI()    
    widget.resize(2000, 1000)
    widget.show()

    sys.exit(app.exec())