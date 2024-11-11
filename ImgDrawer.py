import sys
import time
import random
from PySide6.QtCore import SIGNAL
from PySide6 import QtCore, QtWidgets, QtGui # -*- coding: utf-8 -*-
from PIL import ImageColor, Image, ImageDraw, ImageQt
from PySide6.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QLabel, QGridLayout, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QRect, QRectF
from PySide6.QtGui import QPalette, QBrush, QPen, QColor, QPainter, QPixmap, QImage
from PySide6.QtOpenGL import *

PATH = '/home/goo/Images/'
PIXSIZE = 3   

from PySide6 import QtCore, QtGui, QtWidgets
XCOORDOFFSET= -0.37
YCOORDOFFSET= -0.4

XOFFSET = 0.37
YOFFSET = 0.4
SCALE_FACTOR = 1.25

class ColorLimit(QtWidgets.QWidget):
    def __init__(self, colorName= "grey", low = -2000.0, high = 2000.0):
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(60, 60, 60))
        pal.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))  
        pal.setColor(QPalette.Button, QColor(60, 60, 60))
        pal.setColor(QPalette.Text, QColor(255, 255, 255))
        
        
        self.lLimit = low
        self.hLimit = high
        self.colorName = colorName
        
        self.GroupBox = QtWidgets.QGroupBox()
        self.GroupBox.setGeometry(0,0,25,25)
        palette = self.GroupBox.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(103, 113, 121))     
        self.GroupBox.setPalette(palette)
        
        mainLayout = QtWidgets.QGridLayout()
        
        self.lbl = QtWidgets.QLabel() 
        self.lbl.setText(str(" < " + self.colorName + " < "))     
        self.lbl.setGeometry(0,0,25,25)
        palette = self.lbl.palette()
        r,g,b = ImageColor.getrgb(self.colorName)
        palette.setColor(palette.WindowText, QtGui.QColor(r, g, b))
        self.lbl.setPalette(palette)
        
        self.lLimitInputbox = QtWidgets.QLineEdit()
        self.lLimitInputbox.setPalette(pal)
        self.lLimitInputbox.setGeometry(0,0,25,25)
        self.setLlimit(self.lLimit)
        
        self.hLimitInputbox = QtWidgets.QLineEdit()
        self.hLimitInputbox.setPalette(pal)
        self.hLimitInputbox.setGeometry(0,0,25,25)
        self.setHlimit(self.hLimit)
        

        mainLayout.addWidget(self.lLimitInputbox ,0, 0)
        mainLayout.addWidget(self.lbl ,0, 1)
        mainLayout.addWidget(self.hLimitInputbox ,0, 2)
        mainLayout.setRowStretch(0,0)
        mainLayout.setColumnStretch(0,0)
        self.GroupBox.setLayout(mainLayout)
    
        
    def setHlimit(self, val):
        self.hLimit  = val
        self.hLimitInputbox.setText(str(self.hLimit )) 
        
    def getHlimit(self):
        self.hLimit = float(self.hLimitInputbox.text())
        return self.hLimit
    
    def setLlimit(self, val):
        self.lLimit  = val
        self.lLimitInputbox.setText(str(self.lLimit )) 
        
    def getllimit(self):
        self.lLimit = float(self.lLimitInputbox.text())
        return self.lLimit

class PhotoViewer(QtWidgets.QGraphicsView):
    coordinatesChanged = QtCore.Signal(QtCore.QPoint)

    def __init__(self, parent):
        super().__init__(parent)
        self._zoom = 0
        self._pinned = False
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._photo.setShapeMode(
            QtWidgets.QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(
            QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(
            QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def resetView(self, scale=1):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if (scale := max(1, scale)) == 1:
                self._zoom = 0
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height()) * scale
                self.scale(factor, factor)
                if not self.zoomPinned():
                    self.centerOn(self._photo)
                self.updateCoordinates()
    
    def setRectView(self, x=1, y=1, w=10, h=10):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if (scale := max(1, scale)) == 1:
                self._zoom = 0
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height()) * scale
                self.scale(factor, factor)
                if not self.zoomPinned():
                    self.centerOn(self._photo)
                self.updateCoordinates()

    def setPhoto(self, pixmap=None):
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        if not (self.zoomPinned() and self.hasPhoto()):
            self._zoom = 0
        #self.resetView(SCALE_FACTOR ** self._zoom)
        self._photo.show()

    def zoomLevel(self):
        return self._zoom

    def zoomPinned(self):
        return self._pinned

    def setZoomPinned(self, enable):
        self._pinned = bool(enable)

    def zoom(self, step):
        zoom = max(0, self._zoom + (step := int(step)))
        if zoom != self._zoom:
            self._zoom = zoom
            if self._zoom > 0:
                if step > 0:
                    factor = SCALE_FACTOR ** step
                else:
                    factor = 1 / SCALE_FACTOR ** abs(step)
                self.scale(factor, factor)
            else:
                self.resetView()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.zoom(delta and delta // abs(delta))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resetView()

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)

    def updateCoordinates(self, pos=None):
        if self._photo.isUnderMouse():
            if pos is None:
                pos = self.mapFromGlobal(QtGui.QCursor.pos())
            point = self.mapToScene(pos).toPoint()
        else:
            point = QtCore.QPoint()
        self.coordinatesChanged.emit(point)

    def mouseMoveEvent(self, event):
        self.updateCoordinates(event.position().toPoint())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.coordinatesChanged.emit(QtCore.QPoint())
        super().leaveEvent(event)
  
 
        
class  ImgDrawer(QtWidgets.QWidget):
    def __init__(self, dimX=135.7, dimY=72.9):
        super().__init__()
        
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(60, 60, 60))
        pal.setColor(QPalette.WindowText, QtGui.QColor(103, 113, 121))  
        pal.setColor(QPalette.Button, QColor(60, 60, 60))
        pal.setColor(QPalette.Text, QColor(255, 255, 255))
        
        self.setWindowTitle('P2')
        # app.setStyle("Fusion")   
        # palette = QPalette()
        # palette.setColor(QPalette.Window, QColor(53, 53, 53))
        # palette.setColor(QPalette.WindowText,QtGui.QColor(0, 0, 0))
        # app.setPalette(palette)      
        
        self._path = ""
        self.dimX = dimX
        self.dimY = dimY
        self.initImage()
               
        self.blueLimit = ColorLimit(colorName= "blue", low = -2000.0, high = 2000.0)
        self.greenLimit = ColorLimit(colorName= "green", low = -2000.0, high = 2000.0)
        self.yellowLimit = ColorLimit(colorName= "yellow", low = -2000.0, high = 2000.0)
        self.orangeLimit = ColorLimit(colorName= "orange", low = -2000.0, high = 2000.0)
        self.redLimit = ColorLimit(colorName= "red", low = -2000.0, high = 2000.0)
      
        self.setLowLimit()
        self.setHighLimit() 
        
        self.layoutimage = QGridLayout(self)
        self.viewer = PhotoViewer(self)
        self.viewer.coordinatesChanged.connect(self.handleCoords)
        self.labelCoords = QtWidgets.QLabel(self)
        self.labelCoords.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight |
            QtCore.Qt.AlignmentFlag.AlignCenter)
        palette = self.labelCoords.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(254,254,254))
        self.labelCoords.setPalette(palette)
       
        self.buttonOpen = QtWidgets.QPushButton(self)
        self.buttonOpen.setText('Open Image')
        self.buttonOpen.setPalette(pal)
        self.buttonOpen.clicked.connect(self.handleOpen)
        
        self.buttonZoomOut = QtWidgets.QPushButton(self)
        self.buttonZoomOut.setText('Zoom out')
        self.buttonZoomOut.setPalette(pal)
        self.buttonZoomOut.clicked.connect(self.handleZoomOut)       
        
        self.buttonSave = QtWidgets.QPushButton(self)
        self.buttonSave.setText('Save Image')
        self.buttonSave.setPalette(pal)
        self.buttonSave.clicked.connect(self.handleSave) 
        
        self.layoutimage.addWidget(self.viewer,0, 0, 1, 5)
        
        self.layoutimage.addWidget(self.blueLimit.GroupBox,1, 0)
        self.layoutimage.addWidget(self.greenLimit.GroupBox,1,1)
        self.layoutimage.addWidget(self.yellowLimit.GroupBox,1,2)
        self.layoutimage.addWidget(self.orangeLimit.GroupBox,1,3)
        self.layoutimage.addWidget(self.redLimit.GroupBox,1,4)
        
        self.layoutimage.addWidget(self.buttonOpen, 2,1)
        self.layoutimage.addWidget(self.buttonSave, 2,2)
        self.layoutimage.addWidget(self.buttonZoomOut, 2,3)
        self.layoutimage.addWidget(self.labelCoords, 2,4)
        self.layoutimage.setColumnStretch(5,5)
        self.layoutimage.setRowStretch(0,0)
        self.loadImage()
    
    def handleCoords(self, point):
        if not point.isNull():
            x = "{0:.2f}".format((point.x() / self.ratioX)+ XCOORDOFFSET)
            y = "{0:.2f}".format((point.y() / self.ratioY)+ YCOORDOFFSET)
            self.labelCoords.setText(f'x={x}, y={y} (m)')
            #self.labelCoords.setText(f'{point.x()}, {point.y()}')
        else:
            self.labelCoords.clear()

    def handleZoomOut(self):
        self.viewer.resetView()
    
    def handleSave(self):
        if (start := self._path) is None:
            start = QtCore.QStandardPaths.standardLocations(
                QtCore.QStandardPaths.StandardLocation.PicturesLocation)[0]
        if path := QtWidgets.QFileDialog.getSaveFileName(
            self, 'Open Image', start)[0]:
            self._path = path  
            self.saveImage()             
            self.reInitImage(self._path)        
        
        
    def handleOpen(self):
        if (start := self._path) is None:
            start = QtCore.QStandardPaths.standardLocations(
                QtCore.QStandardPaths.StandardLocation.PicturesLocation)[0]
        if path := QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open Image', start)[0]:
            self.labelCoords.clear()
            if not (pixmap := QtGui.QPixmap(path)).isNull():
                self.viewer.setPhoto(pixmap)
                self._path = path
                self.reInitImage( self._path)
                
            else:
                QtWidgets.QMessageBox.warning(self, 'Error',
                    f'<br>Could not load image file:<br>'
                    f'<br><b>{path}</b><br>'
                    )
        

    def setLowLimit(self, blue=-100, green=-200, yellow=-300, orange=-400, red=-600):
        self.blueLimit.setLlimit(blue)
        self.greenLimit.setLlimit(green)
        self.yellowLimit.setLlimit(yellow)
        self.orangeLimit.setLlimit(orange)
        self.redLimit.setLlimit(red)
    
    def setHighLimit(self, blue=0, green=-100, yellow=-200, orange=-300, red=-400):
        self.blueLimit.setHlimit(blue)
        self.greenLimit.setHlimit(green)
        self.yellowLimit.setHlimit(yellow)
        self.orangeLimit.setHlimit(orange)
        self.redLimit.setHlimit(red)
        
    def getLimit(self):
        self.bLow =  self.blueLimit.getllimit()
        self.gLow = self.greenLimit.getllimit()
        self.yLow = self.yellowLimit.getllimit()
        self.oLow = self.orangeLimit.getllimit()
        self.rLow = self.redLimit.getllimit()
        self.bHigh =  self.blueLimit.getHlimit()
        self.gHigh = self.greenLimit.getHlimit()
        self.yHigh = self.yellowLimit.getHlimit()
        self.oHigh = self.orangeLimit.getHlimit()
        self.rHigh = self.redLimit.getHlimit()
        
    def set(self, x=20, y=20, meas=0.0):
        x1 = int(((x+XOFFSET) * self.ratioX) - PIXSIZE/2.0)
        x2 = int(((x+XOFFSET) * self.ratioX) + PIXSIZE/2.0)
        y1 = int(((y+YOFFSET)* self.ratioY) - PIXSIZE/2.0) 
        y2 = int(((y+YOFFSET) * self.ratioY) + + PIXSIZE/2.0)
        transparency = 127    
        self.getLimit()
        if meas > self.bLow and meas < self.bHigh:
            r,g,b = ImageColor.getrgb("blue")
        elif meas > self.gLow and meas < self.gHigh :
            r,g,b = ImageColor.getrgb("green")
        elif meas > self.yLow and meas < self.yHigh :
            r,g,b = ImageColor.getrgb("yellow")
        elif meas > self.oLow and meas < self.oHigh :
            r,g,b = ImageColor.getrgb("orange")        
        elif meas > self.rLow and meas < self.rHigh :
            r,g,b = ImageColor.getrgb("red")
        else:
            r,g,b = ImageColor.getrgb("grey")
        self.draw.rectangle(((x1, y1), (x2, y2)), fill=(r,g,b,transparency))
     
    def initImage(self, _destPath = PATH + 'rgb_image.png'):  
        self.img = Image.open(PATH + 'P2.png')
        
        # gray_img = self.img.convert('L')
        # gray_img.save(PATH + 'goo_gray.png')                
        self.rgb_img = self.img.convert('RGB')
        self._path = _destPath
        self.rgb_img.save(self._path)
        self.width = self.rgb_img.width
        self.height = self.rgb_img.height           
        self.ratioX =  self.width /  self.dimX 
        self.ratioY =  self.height /  self.dimY
        self.draw = ImageDraw.Draw(self.rgb_img, "RGBA")
     
    def reInitImage(self, _path = PATH + 'P2.png'):  
        self.img = Image.open(_path)
        self.rgb_img = self.img.convert('RGB')
        self.width = self.rgb_img.width
        self.height = self.rgb_img.height           
        self.ratioX =  self.width /  self.dimX 
        self.ratioY =  self.height /  self.dimY 
        self._path = _path
        self.rgb_img.save(self._path)
        self.draw = ImageDraw.Draw(self.rgb_img, "RGBA")   
        
        
    def loadImage(self):
        self.labelCoords.clear()
        if not (pixmap := QtGui.QPixmap(self._path)).isNull():
                self.viewer.setPhoto(pixmap)
               # self.reInitImage(self._path)
                

   
    def saveImage(self):
        self.rgb_img.save(self._path)     
        

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    img = ImgDrawer(dimX=135.6, dimY=72.2)
    img.resize(2000, 1000)
    img.show()
    
      

    sys.exit(app.exec())
    
    
