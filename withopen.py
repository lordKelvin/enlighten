import random

def simpleMaze(side=16,unit=20):
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
    for y in xrange(16):
        for x in xrange(16):
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
'''
import lightup, canvas, sys, os
from PIL import Image, ImageSequence

gif = []
for i in xrange(len(player)-1):
    for j in xrange(3):
        p = ((player[i + 1][0] - player[i][0])*j/3+player[i][0], (player[i + 1][1] - player[i][1])*j/3+player[i][1])
        canvas.show(outline, lightup.lightUp(p, outline), p, gif)

from images2gif import writeGif
writeGif("out.gif", gif, duration=len(gif)/1000.0, dither=0)

import subprocess
subprocess.Popen(['eog','out.gif'])
'''
