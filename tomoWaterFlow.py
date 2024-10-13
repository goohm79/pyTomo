import sys
from PySide6.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem
from PySide6.QtCore import Qt, QRect, QRectF
from PySide6.QtGui import QBrush, QPen, QColor, QPainter

from time import sleep

redColor = ((255,200,200),(252,252,12),(252,104,12),(252,60,12))
blueColor = ((200,255,200),(92,252,12),(12,184,252),(12,88,252))

        
        
class TOMOWATERFLOW:
    def __init__(self, x=1000, y=600):
        self.x = x
        self.y = y
        app = QApplication(sys.argv)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setGeometry(0, 0, self.x, self.y)      
        self.view.show()

        None
        
    def map_turtle_to_scene(self, x, y):
        return x + (self.x/2), -y + (self.y/2)  # Adjust offsets as needed
       
    def add_pixel(self, x, y, color):
                # Draw a rectangle item, setting the dimensions.
        # Draw a rectangle item, setting the dimensions.
        rect = QGraphicsRectItem(0, 0, 10, 10)
        
        # Set the origin (position) of the rectangle in the scene.
        rect.setPos(x, y)
        
        # Define the brush (fill).
        brush = QBrush(Qt.GlobalColor.red)
        rect.setBrush(brush)
        
        # Define the pen (line)
        pen = QPen(Qt.GlobalColor.cyan)
        pen.setWidth(1)
        rect.setPen(pen)
        
        self.scene.addItem(rect)
        
        self.scene.update()
        


   
    
    def drawpixel(self, x, y, volt):
        color =self.voltToRGBcolor(volt)
        self.add_pixel(x,y,color)
    
        
    def voltToRGBcolor(self, volt=0.0):
        if volt == 0.0 :
            color = (255,255,255)
        elif volt > 0:

            if volt > 1000:
                color = blueColor[3]
            elif volt > 500:
                color = blueColor[2]
            elif volt > 250:
                color = blueColor[1]
            elif volt > 0:
                color = blueColor[0]
        else :
            volt = -1 * volt
            if volt > 1000:
                color = redColor[3]
            elif volt > 500:
                color = redColor[2]
            elif volt > 250:
                color = redColor[1]
            elif volt > 0:
                color = redColor[0]
            
        return color


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dut = TOMOWATERFLOW(x=600,y=400)
    x = 0
    z = 0
    dut.drawpixel(100,100,(100*-10))
    while x <100:
        x= x +4
        for y in range(60):
            if z == 1:
                y = 60 - y
            else:
                z=0
            dut.drawpixel(x,y,(x*-10))
            dut.drawpixel(x+1,y,(x*-20))
            dut.drawpixel(x+2,y,(x*10))
            dut.drawpixel(x+3,y,(x*20))
            sleep(0.1)
        if z == 0:
            z=1
        else:
            z=0
    sleep(1)
    

