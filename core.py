from PyQt4.QtGui import *
from PyQt4.QtCore import *
from painter import Painter
import random



class Core(object):
    def afterInit(self):
        self.painter=Painter(self.app.scene)
        self.app.painter=self.painter
        self.api=self.app.api

    def main(self):
        self.drawMaze(self.gen_maze())
        self.drawLight()

    def gen_maze(self):
        maze = self.simpleMaze(side=int(self.app.config.options.side),unit=int(self.app.config.options.unit))
        self.maze=maze
        return maze

    def drawMaze(self, maze):
        self.map=self.painter.polygon(maze,width=2)

        x=maze[0][0]-int(self.app.config.options.unit)
        y=maze[0][1]
        self.player=self.painter.player(QPointF(x,y))

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


    def lightUp(self,player, outline):
        visible = []
        u = player
        for i, c in enumerate(outline):
            c0 = outline[i - 1]
            c2 = outline[(i + 1) % len(outline)]
            rib0 = (c0[0] - c[0]) * u[1] - (c0[1] - c[1]) * u[0] > c0[0] * c[1] - c0[1] * c[0]
            rib1 = (c[0] - c2[0]) * u[1] - (c[1] - c2[1]) * u[0] > c[0] * c2[1] - c[1] * c2[0]
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
                    m = (C[0] * X[1] - C[1] * X[0]) / float( div )
                    if k > 0 and m == 1:
                        n3 = outline[(j + 1) % len(outline)]
                        one = (n1[0] - n2[0]) * u[1] - (n1[1] - n2[1]) * u[0] > n1[0] * n2[1] - n1[1] * n2[0]
                        two = (n2[0] - n3[0]) * u[1] - (n2[1] - n3[1]) * u[0] > n2[0] * n3[1] - n2[1] * n3[0]
                        if one == two:
                            if k < 1:
                                fail = True
                                break
                            else:
                                if kmin == 0 or kmin > k:
                                    kmin = k

                    if k > 0 and m > 0 and m < 1:
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
    #    player = []

        def possible(x, y):
            if f[x][y] != 0:
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
            f[x][y] = 1;
     #       player.append((unit * x + unit / 2, unit * y - unit / 2))

            d = []
            if possible(x + 1, y): d.append(0)
            if possible(x, y + 1): d.append(90)
            if possible(x - 1, y): d.append(180)
            if possible(x, y - 1): d.append(270)

            if not d:
                break

            a = d[random.randint(0, len(d) - 1)]
            if a == 0: x += 1
            elif a == 90: y += 1
            elif a == 180: x -= 1
            elif a == 270: y -= 1

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

        self.api.info('Maze generation done!')
        return outline