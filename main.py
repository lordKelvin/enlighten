#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from painter import Player
from snowflake import *

from PyQt4.QtGui import *
from PyQt4.QtCore import *

starttime = datetime.now()
icons = loadIcons(cwd + 'icons/')

from winterQt import WinterQtApp, API

__author__ = 'averrin, lordKelvin' # >:(

class Scene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.coord=''
        self.init()

    def init(self):
        del self.coord
        self.coord = self.drawText('', 0, 0)


#    def dragEnterEvent(self, event):
#        item = event.mimeData().Player
#        tempPixmap = QPixmap(item.pixmap())
#        painter = QPainter()
#        painter.begin(tempPixmap)
#        painter.fillRect(item.pixmap().rect(), QColor(127, 127, 127, 127))
#        painter.end()
#        item.setPixmap(tempPixmap)


    def dragLeaveEvent(self, event):
        item = event.mimeData().Player

        pixmap = QPixmap(event.mimeData().imageData())
        item.setPixmap(pixmap)


    def dragMoveEvent(self, ev):
        item = self.itemAt(ev.scenePos().x(), ev.scenePos().y())
        #        if item==self.app.core.light:
        #            self.removeItem(self.app.core.light)
        #        item = self.itemAt(ev.scenePos().x(),ev.scenePos().y())
        #        if item == self.app.core.map:
        if item == self.app.core.map or item == self.app.core.light:
            self.app.core.redrawLight(ev.scenePos())
        #            self.app.core.player.setPos(ev.scenePos())


    def dropEvent(self, event):
        pixmap = QPixmap(event.mimeData().imageData())
        item = Player(pixmap, None, self)

        item.setPos(event.scenePos() - event.mimeData().Pos)
        item.setZValue(event.mimeData().z)

        self.removeItem(event.mimeData().Player)
        self.app.core.player = item


    def drawText(self, text, x, y):
        item = QGraphicsTextItem(text)
        self.addItem(item)
        item.setY(x)
        item.setX(y)
        return item

class UI(WinterQtApp):
    def __init__(self):
        WinterQtApp.__init__(self)

    def _afterMWInit(self):
        self.scene = Scene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.mousePressEvent = self.mousePressEvent
        self.graphicsView.mouseReleaseEvent = self.mouseReleaseEvent
        self.graphicsView.mouseMoveEvent = self.mouseMoveEvent

        self.scene.app = self


    def _afterAppInit(self):
        self.scene.setBackgroundBrush(QBrush(QColor(self.config.options.scene_bg_color)))


    def keyPressEvent(self, event):
    #        print(event.key())
        if event.key() == 16777216:
            QMainWindow.close(self)
        elif event.key() in [87, 16777235]:
            self.core.n()
        elif event.key() in [83, 16777237]:
            self.core.s()
        elif event.key() in [65, 16777234]:
            self.core.w()
        elif event.key() in [68, 16777236]:
            self.core.e()


    def refresh(self):
        item = self.scene.itemAt(self.core.player.x(), self.core.player.y())
        if item == self.core.map or item == self.core.light:
            self.core.redrawLight(QPointF(self.core.player.x() + 5, self.core.player.y() + 5))


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
            self.api.error(e)


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