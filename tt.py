#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
from snowflake import loadIcons


cwd = sys.path[0] + '/'
icons = loadIcons(cwd+'icons/')

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(300, 300, 600, 500)

        # создание сцены для отображения элементов-рисунков:
        self.scene = Scene()
        # создание виджета представления для отображения сцены:
        view = QtGui.QGraphicsView(self.scene, self)
        # параметры качества прорисовки для виджета представления:
        view.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        view.setBackgroundBrush(QtGui.QColor(0, 128, 64)) # цвет фона представления
        self.setCentralWidget(view) # размещение виджета представления в главном окне

        # первый элемент:
        item = Element(QtGui.QPixmap(icons['red']), None, self.scene)
        item.setZValue(1)

        # второй элемент (изначально - с поворотом)
        item2 = Element(QtGui.QPixmap(icons['red']), None, self.scene)
        item2.rotate(25) # поворот
        item2.setPos(100, 20) # позиция элемента
        item2.setZValue(2)

class Scene(QtGui.QGraphicsScene):
    def __init__(self, parent = None):
        QtGui.QGraphicsScene.__init__(self, parent)

    # операция drag and drop входит в область сцены
    def dragEnterEvent(self, event):
        item = event.mimeData().Element
        # временный "затемнённый" рисунок перетаскиваемой картинки:
        tempPixmap = QtGui.QPixmap(item.pixmap())
        painter = QtGui.QPainter()
        painter.begin(tempPixmap)
        painter.fillRect(item.pixmap().rect(), QtGui.QColor(127, 127, 127, 127))
        painter.end()
        item.setPixmap(tempPixmap)

    # операция drag and drop покидает область сцены
    def dragLeaveEvent(self, event):
        item = event.mimeData().Element
        # восстанавливаем рисунок перетаскиваемой картинки:
        pixmap = QtGui.QPixmap(event.mimeData().imageData())
        item.setPixmap(pixmap)

    # в процессе выполнения операции drag and drop
    def dragMoveEvent(self, event):
        pass

    # завершение операции drag and drop
    def dropEvent(self, event):
        # создание копии перенесённого элемента на новом месте:
        pixmap = QtGui.QPixmap(event.mimeData().imageData())
        item = Element(pixmap, None, self)
        # установка положения элемента,
        # координаты курсора мыши на сцене корректируем координатами курсора мыши на элементе:
        item.setPos(event.scenePos() - event.mimeData().Pos)
        item.setZValue(event.mimeData().z) # установка Z-положения элемента
        # удаление перенесённого элемента:
        self.removeItem(event.mimeData().Element)

class Element(QtGui.QGraphicsPixmapItem):
    def __init__(self, pixmap, parent = None, scene = None):
        QtGui.QGraphicsPixmapItem.__init__(self, pixmap, parent, scene)
        self.setTransformationMode(QtCore.Qt.SmoothTransformation) # качество прорисовки
        self.setCursor(QtCore.Qt.OpenHandCursor) # вид курсора мыши над элементом
        #self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton: # только левая клавиша мыши
            event.ignore()
            return
        drag = QtGui.QDrag(event.widget()) # объект Drag
        mime = QtCore.QMimeData()
        mime.setImageData(QtCore.QVariant(self.pixmap())) # запоминаем рисунок
        mime.Pos = event.pos() # запоминаем позицию события в координатах элемента
        mime.z = self.zValue() # запоминаем z-позицию рисунка
        mime.Element = self # запоминаем сам элемент, который переносится
        # примечание: предыдущие три "запоминания" можно реализовать
        # и с помощью более "понятного" mime.setData(),
        # особенно, если нужно передавать данные не только в пределах одного приложения
        # (тогда использование mime.setData() будет даже предпочтительнее)
        drag.setMimeData(mime)

        drag.setPixmap(self.pixmap()) # рисунок, отображающийся в процессе переноса
        drag.setHotSpot(event.pos().toPoint()) # позиция "ухватки"

        drag.start() # запуск (начало) перетаскивания

if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())