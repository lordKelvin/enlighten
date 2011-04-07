import lightup, canvas
import random

f = []
for i in xrange(16):
    f.append([])
    for j in xrange(16):
        f[i].append(0 if i % 15 and j % 15 else 2)

x = random.randint(1, 14)
y = random.randint(1, 14)
player = []

def possible(x, y):
    if f[x][y] != 0:
        return False
    S = 0
    if f[x + 1][y] == 1: S += 1
    if f[x][y + 1] == 1: S += 1
    if f[x - 1][y] == 1: S += 1
    if f[x][y - 1] == 1: S += 1

    return S <= 1

while True:
    f[x][y] = 1;
    player.append((20 * x + 10, 20 * y - 10))
    
    d = []
    if possible(x + 1, y): d.append(0)
    if possible(x, y + 1): d.append(90)
    if possible(x - 1, y): d.append(180)
    if possible(x, y - 1): d.append(270)
    
    if not d:
        break
    
    a = d[random.randint(0, len(d) - 1)]
    if a == 0: x += 1
    if a == 90: y += 1
    if a == 180: x -= 1
    if a == 270: y -= 1

for y in xrange(16-1):
    for x in xrange(16-1):
        if f[x][y] == 1 and f[x+1][y+1] == 1 and f[x][y+1] == 0 and f[x+1][y] == 0:
            f[x][y+1] = 1
        if f[x][y] == 0 and f[x+1][y+1] == 0 and f[x][y+1] == 1 and f[x+1][y] == 1:
            f[x][y] = 1
    
vec = []   
for y in xrange(16):
    for x in xrange(16):
        if f[x][y] == 1:
            vec.append(((20 * x, 20 * y), (20 * x + 20, 20 * y)))
            vec.append(((20 * x, 20 * y), (20 * x, 20 * y - 20)))
            vec.append(((20 * x, 20 * y - 20), (20 * x + 20, 20 * y - 20)))
            vec.append(((20 * x + 20, 20 * y), (20 * x + 20, 20 * y - 20)))
            
vec = sorted(vec)
i = 0
while i + 1 < len(vec):
    if vec[i] == vec[i+1]:
        vec.pop(i+1)
        vec.pop(i)
    else: i += 1

i = 0
while i < len(vec):
    j = i + 1
    while j < len(vec):
        if vec[i][1] == vec[j][0]:
            if (vec[i][0][0] == vec[i][1][0]) == (vec[j][0][0] == vec[j][1][0]):
                s2 = vec.pop(j)[1]
                s1 = vec.pop(i)[0]
                vec.insert(i, (s1, s2))
                continue
        if vec[i][0] == vec[j][1]:
            if (vec[i][0][0] == vec[i][1][0]) == (vec[j][0][0] == vec[j][1][0]):
                s1 = vec.pop(j)[0]
                s2 = vec.pop(i)[1]
                vec.insert(i, (s1, s2))
                continue
        j += 1
    i += 1

v = [vec.pop(0)]
while vec:
    for i, e in enumerate(vec):
        if v[-1][1] == e[0]:
            v.append(vec.pop(i))
            break
        if v[-1][1] == e[1]:
            t = vec.pop(i)
            v.append((t[1], t[0]))
            break
        if v[0][0] == e[1]:
            v.insert(0, vec.pop(i))
            break
        if v[0][0] == e[0]:
            t = vec.pop(i)
            v.insert(0, (t[1], t[0]))
            break
    else:
        vec = []
vec = v

outline = []
for i in xrange(len(vec)):
    if vec[i - 1][1] == vec[i][0]:
        outline.append(vec[i - 1][0])
    else:
        raise Exception("i = %d\nvec[i - 1] = %s\nvec[i] = %s" % (i, vec[i - 1 ], vec[i]) )

from PIL import Image, ImageSequence
import sys, os

gif = []
for i in xrange(len(player)-1):
    for j in xrange(3):
        p = ((player[i + 1][0] - player[i][0])*j/3+player[i][0], (player[i + 1][1] - player[i][1])*j/3+player[i][1])
        canvas.show(outline, lightup.lightUp(p, outline), p, gif)

from images2gif import writeGif
writeGif("out.gif", gif, duration=len(gif)/1000.0, dither=0)

import subprocess

subprocess.Popen(['/usr/bin/eog','out.gif'])
