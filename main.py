#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import os
import re
import sys
from painter import Player
from snowflake import *

from PyQt4.QtGui import *
from PyQt4 import uic
from PyQt4.QtCore import *

starttime = datetime.now()
icons = loadIcons(cwd+'icons/')

from winterQt import WinterQtApp, API

__author__ = 'averrin' # >:(

class Scene(QGraphicsScene):
    def __init__(self, parent = None):
        QGraphicsScene.__init__(self, parent)
        self.init()

    def init(self):
        self.coord=self.drawText('boom', 0, 0)


    def dragEnterEvent(self, event):
        item = event.mimeData().Player

        tempPixmap = QPixmap(item.pixmap())
        painter = QPainter()
        painter.begin(tempPixmap)
        painter.fillRect(item.pixmap().rect(), QColor(127, 127, 127, 127))
        painter.end()
        item.setPixmap(tempPixmap)


    def dragLeaveEvent(self, event):
        item = event.mimeData().Player

        pixmap = QPixmap(event.mimeData().imageData())
        item.setPixmap(pixmap)


    def dragMoveEvent(self, ev):
        item = self.itemAt(ev.scenePos().x(),ev.scenePos().y())
#        if item==self.app.core.light:
#            self.removeItem(self.app.core.light)
#        item = self.itemAt(ev.scenePos().x(),ev.scenePos().y())
#        if item == self.app.core.map:
        if item == self.app.core.map or item==self.app.core.light:
            self.app.core.redrawLight(ev.scenePos())



    def dropEvent(self, event):

        pixmap = QPixmap(event.mimeData().imageData())
        item = Player(pixmap, None, self)


        item.setPos(event.scenePos() - event.mimeData().Pos)
        item.setZValue(event.mimeData().z)

        self.removeItem(event.mimeData().Player)


    def drawText(self, text, x, y):
        item = QGraphicsTextItem(text)
        self.addItem(item)
        item.setY(x)
        item.setX(y)
        return item

class UI(WinterQtApp):
    def __init__(self):
        WinterQtApp.__init__(self)

    def afterMWInit(self):
        self.scene = Scene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.mousePressEvent = self.mousePressEvent
        self.graphicsView.mouseReleaseEvent = self.mouseReleaseEvent
        self.graphicsView.mouseMoveEvent = self.mouseMoveEvent

        self.scene.app=self





    def mousePressEvent(self, ev):
        if ev.buttons() == Qt.LeftButton:
            QGraphicsView.mousePressEvent(self.graphicsView, ev)
        self.mouse = [ev.pos().x(), ev.pos().y()]

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            QGraphicsView.mouseReleaseEvent(self.graphicsView, ev)

    def mouseMoveEvent(self, ev):
        self.mouse = [ev.pos().x(), ev.pos().y()]
        try:
            item = self.scene.itemAt(self.mouse[0], self.mouse[1])
            self.scene.coord.setHtml('<span style="color:green;background:black;">%d,%d -- %s</span>' % (
            self.mouse[0], self.mouse[1], item))

        except Exception, e:
            self.error(e)


    def dragEnterEvent(self, event):
        item = event.mimeData().Player

        tempPixmap = QPixmap(item.pixmap())
        painter = QPainter()
        painter.begin(tempPixmap)
        painter.fillRect(item.pixmap().rect(), QColor(127, 127, 127, 127))
        painter.end()
        item.setPixmap(tempPixmap)


    def dragLeaveEvent(self, event):
        item = event.mimeData().Player

        pixmap = QPixmap(event.mimeData().imageData())
        item.setPixmap(pixmap)


    def dragMoveEvent(self, event):
        pass


    def dropEvent(self, event):

        pixmap = QPixmap(event.mimeData().imageData())
        item = Player(pixmap, None, self)


        item.setPos(event.scenePos() - event.mimeData().Pos)
        item.setZValue(event.mimeData().z)

        self.removeItem(event.mimeData().Player)



def main():
    qtapp = QApplication(sys.argv)
    ui = UI()

    ui.show()
    api = API()

    endtime = datetime.now()
    delta = endtime - starttime
    api.info('Initialization time: %s' % delta)
    qtapp.exec_()


if __name__ == '__main__':
    main()