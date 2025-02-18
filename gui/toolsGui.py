import sys
import serial.tools.list_ports
import time
import json

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

class PARAMGUI(QtWidgets.QWidget):
    def __init__(self, project= "Pilote"):
        self.projectParam = project
        self.listJsonAllParam = ""
        if self.projectParam == "Pilote":
            self.fileName= "paramPilote.json"
            self.ReadJsonParam()
        
    def CreatePiloteJsonParam(self):
        newParam = {
              "Project": "P2_Pilote",
              
              "Log_State": 1,
              
              "Polarisation_State": 1,
            
              "PL303_State": 1,
            
              "PL303_Ilim": 1000,
            
              "PL303_Vlim": 10,
            
              "CSVfilePath": "/home/goo/github/pyTomo/Dataslog.csv",
              },
        with open(self.fileName, mode="w", encoding="utf-8") as write_file: json.dump(newParam, write_file)
             
        
    def SetJsonParam(self, name="", val=""): 
        self.listJsonAllParam[0][name]=val
        self.WriteJsonParam()
        
    def GetJsonParam (self, name =""): 
        return self.listJsonAllParam[0].get(name)
     
    def ReadJsonParam(self):           
        with open(self.fileName, 'r') as f: ret = json.load(f)
        self.listJsonAllParam = ret
        return ret
        
    def WriteJsonParam(self):   
        with open(self.fileName, mode="w", encoding="utf-8") as write_file: json.dump(self.listJsonAllParam, write_file)
            
        

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
        
class SDIGIT(QtWidgets.QWidget):
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
        
        mainLayout = QtWidgets.QGridLayout()
        
        mainLayout.addWidget(self.lbl,0, 0)
        mainLayout.addWidget(self.lcd,1, 0, 1, 1)
        mainLayout.setRowStretch(1,1)
        self.GroupBox.setLayout(mainLayout)
    
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
        
if __name__ == "__main__":
    dut = PARAMGUI()
    dut.CreatePiloteJsonParam()
    dut.ReadJsonParam()
    dut.SetJsonParam(name="Project",val="roro")
    dut.WriteJsonParam()
    dut.ReadJsonParam()
    print(dut.GetJsonParam(name="Project"))
  
