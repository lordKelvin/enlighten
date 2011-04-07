from PyQt4.QtGui import *
from PyQt4.QtCore import *
from painter import Painter
import random
import math


class Core(object):
    def afterInit(self):
        self.painter=Painter(self.app.scene)
        self.app.painter=self.painter

    def main(self):
        self.drawMaze(self.gen_maze())
        self.drawLight()

    def gen_maze(self):
        maze = self.simpleMaze(side=int(self.app.config.options.side),unit=int(self.app.config.options.unit))
        [self.B, self.N] = self.fasterThenEver(maze)
        self.maze = maze
        return maze

    def drawMaze(self, maze):
        self.map=self.painter.polygon(maze,width=2)

        i = random.randint(0, len(maze) - 1)
        l = int( self.app.config.options.unit ) / (2 * math.hypot(self.B[i - 1][0], self.B[i - 1][1]))
        megax = (maze[i - 1][0] + maze[i][0]) / 2 - self.B[i - 1][1] * l
        megay = (maze[i - 1][1] + maze[i][1]) / 2 + self.B[i - 1][0] * l
        self.player=self.painter.player(QPointF(megax, megay))

    def regen_maze(self):
        self.app.scene.clear()
        self.app.scene.init()
        self.drawMaze(self.gen_maze())
        self.drawLight()
        self.api.info('Maze regenerated')

    def drawLight(self,coord=''):
        if not coord:
            coord=self.player
        coord=(coord.x(),coord.y())
            
        self.light=self.painter.polygon(self.lightUp(coord,self.maze),'yellow',0,'yellow', 0.5)

    def redrawLight(self,pos):
        self.app.scene.removeItem(self.light)
        self.drawLight(pos)

    def fasterThenEver(self,outline):
        B = [] # B[ n ]: from outline[ n ] to outline[ n + 1 ]
        N = [] # N[ n ]: outline[i - 1] x outline[i]
        for i in xrange(len(outline)):
            inext = outline[(i + 1) % len(outline)]
            B.append((inext[0] - outline[i][0], inext[1] - outline[i][1]))
            N.append(outline[i][0] * inext[1] - outline[i][1] * inext[0])
        return B, N

    def lightUp(self,player,outline):
        visible = []
        u = player
        for i, c in enumerate(outline):
            rib0 = self.B[i - 1][1] * u[0] - self.B[i - 1][0] * u[1] > self.N[i - 1]
            rib1 = self.B[i][1] * u[0] - self.B[i][0] * u[1] > self.N[i]
            fail = False
            kmin = 0
            for j, n2 in enumerate(outline):
                n1 = outline[j - 1]
                C = (c[0] - u[0], c[1] - u[1])
                B = (n2[0] - n1[0], n2[1] - n1[1])
                X = (u[0] - n1[0], u[1] - n1[1])
                div = C[0] * B[1] - C[1] * B[0]
                if div:
                    k = (B[0] * X[1] - B[1] * X[0]) / float( div )
                    if k > 0:
                        m = (C[0] * X[1] - C[1] * X[0]) / float( div )
                        if m == 1:
                            n3 = outline[(j + 1) % len(outline)]
                            one = (n2[1] - n1[1]) * u[0] - (n2[0] - n1[0]) * u[1] > n1[0] * n2[1] - n1[1] * n2[0]
                            two = (n3[1] - n2[1]) * u[0] - (n3[0] - n2[0]) * u[1] > n2[0] * n3[1] - n2[1] * n3[0]
                            if one == two:
                                if k < 1:
                                    fail = True
                                    break
                                else:
                                    if kmin == 0 or kmin > k:
                                        kmin = k

                        if m > 0 and m < 1:
                            if k < 1:
                                fail = True
                                break
                            else:
                                if kmin == 0 or kmin > k:
                                    kmin = k
            if not fail:
                extra = ()
                if rib0 != rib1:
                    extra = (int(u[0] + C[0] * kmin + .5), int(u[1] + C[1] * kmin + .5))
                    if rib0:
                        visible.append(extra)

                visible.append(c)

                if not rib0 and rib1:
                    visible.append(extra)
        return visible


    def simpleMaze(self,side=36,unit=20):
        f = []
        for i in xrange(side):
            f.append([])
            for j in xrange(side):
                f[i].append(0 if i % (side - 1) and j % (side - 1) else 2)

        x = random.randint(1, side - 2)
        y = random.randint(1, side - 2)

        def possible(x, y):
            if f[x][y]:
                return False
            s = [f[x + 1][y + 1], f[x][y + 1], f[x - 1][y + 1], f[x - 1][y], f[x - 1][y - 1], f[x][y - 1], f[x + 1][y - 1], f[x + 1][y]]
            for i in (0, 2, 4, 6):
                if s[i - 1] != 1 and s[i] == 1 and s[i + 1] != 1:
                    return False
            S = 0
            for i in (1, 3, 5, 7):
                if s[i] == 1:
                    S += 1
            return S < 2

        while True:
            f[x][y] = 1
            d = []
            if possible(x + 1, y): d.append([x + 1, y])
            if possible(x, y + 1): d.append([x, y + 1])
            if possible(x - 1, y): d.append([x - 1, y])
            if possible(x, y - 1): d.append([x, y - 1])

            if not d:
                break
            [x, y] = d[random.randint(0, len(d) - 1)]

        vec = []
        for y in xrange(side):
            for x in xrange(side):
                if f[x][y] == 1:
                    vec.append(((unit * x, unit * y), (unit * x + unit, unit * y)))
                    vec.append(((unit * x, unit * y), (unit * x, unit * y - unit)))
                    vec.append(((unit * x, unit * y - unit), (unit * x + unit, unit * y - unit)))
                    vec.append(((unit * x + unit, unit * y), (unit * x + unit, unit * y - unit)))

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
                        tmp = vec.pop(j)[1]
                        vec.insert(i, (vec.pop(i)[0], tmp))
                        continue
                if vec[i][0] == vec[j][1]:
                    if vec[j][0][0] == vec[i][1][0] or vec[j][0][1] == vec[i][1][1]:
                        tmp = vec.pop(j)[0]
                        vec.insert(i, (tmp, vec.pop(i)[1]))
                        continue
                j += 1
            i += 1

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
                vec = []

        if v[0][0] == v[-1][1]:
            outline.append(v[0][0])

        return outline