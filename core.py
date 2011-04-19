from PyQt4.QtGui import *
from PyQt4.QtCore import *
from painter import Painter
import random
import math
from winterQt import API
from winterBug import try_this
#from profilehooks import profile
# pip install profilehook; apt-get install python-profiler
# use @profile decorator for profiling function. lightUp is soooo sloooow
from cmaze import *

class Core(object):
    def afterInit(self):
        self.painter = Painter(self.app.scene)
        self.app.painter = self.painter
        self.api = API()

    def main(self):
        self.drawMaze(self.genMaze())
        self.drawLight()
#        self.app.graphicsView.centerOn(QPointF(self.player.x(), self.player.y()))

    def genMaze(self):
        self.maze = self.simpleMaze(side=self.app.config.options.side, unit=self.app.config.options.unit)
#        [self.B, self.N] = self.fasterThenEver(self.maze)
        return self.maze
#    @try_this(API())
    def drawMaze(self, maze):
        self.map = self.painter.polygon(maze, width=2, bg_color=self.app.config.options.maze_bg_color,is_maze=True)

        i = random.randrange(len(maze))
#        l = self.app.config.options.unit / (2 * math.hypot(self.B[i - 1][0], self.B[i - 1][1]))
#        megax = (maze[i - 1][0] + maze[i][0]) / 2 - self.B[i - 1][1] * l
#        megay = (maze[i - 1][1] + maze[i][1]) / 2 + self.B[i - 1][0] * l
        self.player = self.painter.player(QPointF(100,100))
#        self.app.graphicsView.centerOn(QPointF(megax, megay))
#    @try_this(API())
    def regenMaze(self):
        self.app.scene.clear()
        self.app.scene.init()
        del self.light
        del self.player
        del self.map
        self.drawMaze(self.genMaze())
        self.drawLight()
        self.api.info('Maze regenerated')

#    @try_this(API())
    def drawLight(self, coord=''):
        if not coord:
            coord = self.player
        coord = (coord.x(), coord.y())

        self.light = self.painter.polygon(self.lightUp(coord, self.maze), 'yellow', 0, 'yellow', 0.5)

    def redrawLight(self, pos):
        self.app.scene.removeItem(self.light)
        del self.light
        self.drawLight(pos)
    @try_this(API())
    def canMove(self, dx, dy):
        for i, b in enumerate(self.B):
            div = dx * self.B[i][1] - dy * self.B[i][0]
            if div:
                px = self.player.ox() + 10 - self.maze[i][0]
                py = self.player.oy() + 10 - self.maze[i][1]
                k = (py * self.B[i][0] - px * self.B[i][1]) / float(div)
                if k > 0 and k <= 1:
                    n = (py * dx - px * dy) / float(div)
                    if n >= 0 and n <= 1:
                        return False
        return True

    def n(self):
        if self.canMove(0, -10):
            self.player.moveBy(0, -10)
            self.app.refresh()

    def w(self):
        if self.canMove(-10, 0):
            self.player.moveBy(-10, 0)
            self.app.refresh()

    def e(self):
        if self.canMove(10, 0):
            self.player.moveBy(10, 0)
            self.app.refresh()

    def s(self):
        if self.canMove(0, 10):
            self.player.moveBy(0, 10)
            self.app.refresh()


#    @try_this(API())
    def lightUp(self, player, maze):
        keypoints = []
        P = player

        for ray in maze:
            for N in ray:

                A = (N[0] - P[0], N[1] - P[1])
                kmin = None
                semipass = 0
                viewBlocked = False

                for plank in maze:
                    L = plank[-1]
                    for M in plank:

                        B = (M[0] - L[0], M[1] - L[1])
                        C = (L[0] - P[0], L[1] - P[1])
                        L = M
                        div = A[0] * B[1] - A[1] * B[0]
                        if div > 0:
                            n = (C[0] * A[1] - C[1] * A[0])
                            if n >= 0 and n <= div:
                                k = (C[0] * B[1] - C[1] * B[0])
                                if k > 0:
                                    if k < div:
                                        kmin = None
                                        viewBlocked = True
                                        break
                                    if k == div:
                                        if semipass:
                                            kmin = 1
                                        if n:
                                            semipass += 1
                                        else:
                                            semipass -= 1
                                    if k > div: # and n and n != div:
                                        k /= float(div)
                                        if kmin is None or kmin > k:
                                            kmin = k
                    if viewBlocked:
                        break

                if kmin is not None:
                    R =(P[0] + kmin * A[0], P[1] + kmin * A[1])
                    if semipass == 0:
                        keypoints.append(N)
                    elif semipass < 0:
                        keypoints.append(N + R)
                    else:
                        keypoints.append(R + N)
    #                print int( atan2(kmin * A[1], kmin * A[0]) * 57.2957 + 360 ) % 360, int(hypot(kmin * A[0], kmin * A[1])), semipass

        keypoints.sort(key=lambda p: atan2(p[1] - player[1], p[0] - player[0]))
        i = 0
        while i < len(keypoints):
            if len(keypoints[i]) == 4:
                tmp = keypoints.pop(i)
                keypoints.insert(i,(tmp[0], tmp[1]))
                keypoints.insert(i,(tmp[2], tmp[3]))
                i += 2
            else: i += 1
        return keypoints

#    @try_this(API())
    def simpleMaze(self, side=36, unit=20):
        f = aMaze(side, 50, 75)
    #    view(f)
        vec = []
        for y in xrange(side + 1):
            for x in xrange(side + 1):
                if f[x][y]:
                    vec.append(((unit * x, unit * y), (unit * x + unit, unit * y)))
                    vec.append(((unit * x, unit * y), (unit * x, unit * y + unit)))
                    vec.append(((unit * x, unit * y + unit), (unit * x + unit, unit * y + unit)))
                    vec.append(((unit * x + unit, unit * y), (unit * x + unit, unit * y + unit)))

        vec = sorted(vec)
        i = 0
        while i + 1 < len(vec):
            if vec[i] == vec[i + 1]:
                vec.pop(i + 1)
                vec.pop(i)
            else: i += 1

        i = 0
        while i + 1 < len(vec):
            j = i + 1
            while j < len(vec):
                if vec[i][1] == vec[j][0]:
                    if vec[i][0][0] == vec[j][1][0] or vec[i][0][1] == vec[j][1][1]:
    #                    tmp = vec.pop(j)[1]
    #                    vec.insert(i, (vec.pop(i)[0], tmp))
                        vec.insert(i, (vec.pop(i)[0], vec.pop(j - 1)[1]))
                        continue
    #            if vec[i][0] == vec[j][1]:
    #                if vec[j][0][0] == vec[i][1][0] or vec[j][0][1] == vec[i][1][1]:
    #                    tmp = vec.pop(j)[0]
    #                    vec.insert(i, (tmp, vec.pop(i)[1]))
    #                    continue
                j += 1
            i += 1

        vec.append(vec[0])
        outstand = []
        outline = []
        v = [vec.pop(0)]

        while vec:
            for i, e in enumerate(vec):
                if v[-1][1] == e[0]:
                    outline.append(e[0])
                    v.append(vec.pop(i))
                    break
                if v[-1][1] == e[1]:
                    outline.append(e[1])
                    t = vec.pop(i)
                    v.append((t[1], t[0]))
                    break
                if v[0][0] == e[1]:
                    outline.insert(0, e[1])
                    v.insert(0, vec.pop(i))
                    break
                if v[0][0] == e[0]:
                    outline.insert(0, e[0])
                    t = vec.pop(i)
                    v.insert(0, (t[1], t[0]))
                    break
            else:
                if v[0][0] == v[-1][1]:
                    outline.append(v[0][0])
                outstand.append(outline)
                outline = []
                v = [vec.pop(0)]

        if outline:
            outstand.append(outline)

        outstand.pop(0)
        outstand[0].reverse()
        return outstand
