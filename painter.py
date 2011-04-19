
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.uic.Compiler.qtproxies import QtGui
from snowflake import *

icons = loadIcons(cwd + 'icons/')

class Painter(object):
    def __init__(self, scene):
        self.scene = scene

    def line(self, x1, y1, x2, y2, color='black'):
        line = self.scene.addLine(QLineF(x1, y1, x2, y2), QPen(QColor(color))) # is this a "return" pascal-style? #no. most of qt methods return created object. And i do same (look polygon method below), but this method unused and i missed return statement.

    def polygon(self, maze, fg_color='black', width=5, bg_color='white', alpha=1, is_maze=False):
        points = []
        if is_maze:
            for i,raw in enumerate(maze):
                points.append([])
    #            print i,'::',raw
                for p in raw:
    #                print '==',p
                    try:
                        points[i].append(QPointF(p[0], p[1]))
                    except :
                        pass
        else:
            for p in maze:
                points.append(QPointF(p[0], p[1]))
        pen = QPen(QColor(fg_color))
        pen.setWidth(width)
        color = QColor(bg_color)
        color.setAlphaF(alpha)
        poly=[]
        if is_maze:
            i=0
            for element in points:
                if i:
                    poly.append(self.scene.addPolygon(QPolygonF(element), pen,QBrush(QColor('black'))))
                else:
                    poly.append(self.scene.addPolygon(QPolygonF(element), pen, QBrush(color)))
                    i=1
        else:
            poly=self.scene.addPolygon(QPolygonF(points), pen, QBrush(color))
        return poly

    def player(self, coord):
        player = Player(QPixmap(icons['green']), None, self.scene, coord=coord)
        self.scene.addItem(player)
        return player

class Player(QGraphicsPixmapItem):
    def __init__(self, pixmap, parent=None, scene=None, coord=QPointF(0, 0)):
        QGraphicsPixmapItem.__init__(self, pixmap, parent, scene)
        self.setTransformationMode(Qt.SmoothTransformation)
        self.setCursor(Qt.OpenHandCursor)
        self.setPos(coord)
        self.ox = self.x
        self.oy = self.y

        def x(self):
            return self.ox() + 10

        def y(self):
            return self.oy() + 10

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            return
        drag = QDrag(event.widget())
        mime = QMimeData()
        mime.setImageData(QVariant(self.pixmap()))
        mime.Pos = event.pos()
        mime.z = self.zValue()
        mime.Player = self
        drag.setMimeData(mime)
        drag.setPixmap(self.pixmap())
        drag.setHotSpot(event.pos().toPoint())
        drag.start()


