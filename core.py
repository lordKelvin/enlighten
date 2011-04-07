from PyQt4.QtGui import *
from PyQt4.QtCore import *
from painter import Painter



class Core(object):
    def afterInit(self):
        self.painter=Painter(self.app.scene)
        self.app.painter=self.painter

    def main(self):
        self.drawMaze(self.gen_maze())

    def gen_maze(self):
        maze = [(80, 200), (80, 180), (120, 180), (120, 200), (140, 200), (140, 220), (160, 220), (160, 240), (200, 240),
                (200, 260), (220, 260), (220, 240), (240, 240), (240, 220), (260, 220), (260, 200), (280, 200), (280, 180),
                (220, 180), (220, 100), (300, 100), (300, 140), (280, 140), (280, 120), (240, 120), (240, 160), (300, 160),
                (300, 220), (280, 220), (280, 240), (260, 240), (260, 260), (240, 260), (240, 280), (180, 280), (180, 260),
                (140, 260), (140, 240), (120, 240), (120, 220), (100, 220), (100, 200)]
        return maze

    def drawMaze(self, maze):
        self.painter.polygon(maze)
        self.painter.player(QPointF(230, 168))

    def regen_maze(self):
        self.app.scene.clear()
        self.app.scene.init()
        self.drawMaze(self.gen_maze())
