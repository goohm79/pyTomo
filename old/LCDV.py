import sys
from PySide6 import QtCore, QtWidgets, QtGui# -*- coding: utf-8 -*-
from PySide6.QtGui import QPalette, QColor

class LCDV(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # Force the style to be the same on all OSs:
        app.setStyle("Fusion")
        
        # Now use a palette to switch to dark colors:
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText,QtGui.QColor(0, 0, 0))
        ...
        app.setPalette(palette)


        self.setGeometry(100, 100, 200, 100)
        self.setWindowTitle('QFrame Example')

        self.GroupBox = QtWidgets.QGroupBox(self,"Electrode1")
        self.GroupBox.setGeometry(0,0,200,100)
        
        self.lcdv = QtWidgets.QLCDNumber()
        self.lcdv.setGeometry(0,0,200,100) #QtCore.QRect(10, 5, 10, 5))
        self.lcdv.setObjectName("lcdNumber")
        self.lcdv.setSegmentStyle(self.lcdv.SegmentStyle.Flat)
        # get the palette
        palette = self.lcdv.palette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(49, 140, 231))
        # background color
        # "light" border
        
        palette.setColor(palette.Light, QtGui.QColor(53, 53, 53))
        # "dark" border
        palette.setColor(palette.Dark, QtGui.QColor(53, 53, 53))
        
        self.lbl = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.setText("(mV)")
        self.lbl.setPalette(palette)
        # set the palette
        self.lcdv.setPalette(palette)
        self.lcdv.display(24201)


        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.lcdv)
        layout.addWidget(self.lbl)
        layout.addStretch(1)
        self.GroupBox.setLayout(layout)
        

        
        
    def setText(self, val):  
        self.lbl.setText(val) 
         
        

        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = LCDV()
    widget.show()

    sys.exit(app.exec())