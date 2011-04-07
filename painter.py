# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.uic.Compiler.qtproxies import QtGui
from snowflake import loadIcons

cwd = sys.path[0] + '/'
icons = loadIcons(cwd+'icons/')

class Painter(object):
    def __init__(self,scene):
        self.scene=scene

    def line(self, x1, y1, x2, y2, color='black'):
        line = self.scene.addLine(QLineF(x1, y1, x2, y2), QPen(QColor(color)))
        line.info = 'line -- %s' % (((x1, y1), (x2, y2)))

    def polygon(self, raw, fg_color='black',width=5, bg_color='white'):
        points = []
        for p in raw:
            points.append(QPointF(p[0], p[1]))
        pen=QPen(QColor(fg_color))
        pen.setWidth(width)
        poly = self.scene.addPolygon(QPolygonF(points), pen, QBrush(QColor(bg_color)))
        poly.info = 'poly'
        return poly

    def player(self, coord):
        player=Player(QPixmap(icons['green']),None,self.scene, coord=coord)
        self.scene.addItem(player)
        return player
        
class Player(QGraphicsPixmapItem):
    def __init__(self, pixmap, parent = None, scene = None, coord=QPointF(0,0)):
        QGraphicsPixmapItem.__init__(self, pixmap, parent, scene)
        self.setTransformationMode(Qt.SmoothTransformation) # качество прорисовки
        self.setCursor(Qt.OpenHandCursor) # вид курсора мыши над элементом
        #self.setAcceptDrops(True)
        self.setPos(coord)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton: # только левая клавиша мыши
            event.ignore()
            return
        drag = QDrag(event.widget()) # объект Drag
        mime = QMimeData()
        mime.setImageData(QVariant(self.pixmap())) # запоминаем рисунок
        mime.Pos = event.pos() # запоминаем позицию события в координатах элемента
        mime.z = self.zValue() # запоминаем z-позицию рисунка
        mime.Player = self # запоминаем сам элемент, который переносится
        # примечание: предыдущие три "запоминания" можно реализовать
        # и с помощью более "понятного" mime.setData(),
        # особенно, если нужно передавать данные не только в пределах одного приложения
        # (тогда использование mime.setData() будет даже предпочтительнее)
        drag.setMimeData(mime)

        drag.setPixmap(self.pixmap()) # рисунок, отображающийся в процессе переноса
        drag.setHotSpot(event.pos().toPoint()) # позиция "ухватки"

        drag.start() # запуск (начало) перетаскивания#        circle.mousePressEvent=self.mousePressEvent


