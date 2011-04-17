from random import randrange
from math import atan2, hypot
from PIL import Image, ImageDraw
import os

def view(m):
    for c in m:
        line = ''
        for v in c:
            line += {0: '..', 1: 'XX'}[v]
        print line

def aMaze(size, fullfill, wallshort):
    m = [[1] * (size + 1)]
    for y in xrange(size - 1):
        m.append([1] + [0] * (size - 1) + [1])
    m.append(list(m[0]))

    r = []
    for y in xrange(2, size, 2):
        for x in xrange(2, size, 2):
            r.append((x, y))

    while len(r):
        (startx, starty) = r.pop(randrange(len(r)))
        if m[startx][starty] or randrange(100) > fullfill:
            continue

        (sx, sy) = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}[randrange(4)]

        while not m[startx][starty]:
            m[startx][starty] = 1
            if randrange(100) > wallshort:
                break
            startx += sx
            starty += sy
            m[startx][starty] = 1
            startx += sx
            starty += sy
    return m

def simpleMaze(side=20, unit=20):
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

def beam(maze, player):
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

def field3d(maze):
    for i in xrange(len(maze)):
        for j in xrange(len(maze[i])):
            x = maze[i][j][0] - 210
            y = maze[i][j][1] + 210
            maze[i][j] = (x * 100 / (100 - y) + 210, y * 200 / (y - 100))

def show(maze, player, width=400, height=400):
    img = Image.new("RGB", (width, height), "#000000")
    draw = ImageDraw.Draw(img)
    light = beam(maze, player)

    draw.polygon(maze[0], fill=(70, 50, 15))
    for i in xrange(1, len(maze)):
        draw.polygon(maze[i], fill=(0, 0, 0))

    draw.polygon(light, fill=(12, 100, 0))

#    for i, line in enumerate(light):
#        draw.line(player + line, fill=(50, 200, 0))
#        draw.text(line, str(i), fill=(200, 0, 50))
        
    for poly in maze:
        for i in xrange(len(poly)):
            if (poly[i - 1][0] - player[0]) * (poly[i][1] - poly[i - 1][1]) - (poly[i - 1][1] - player[1]) * (poly[i][0] - poly[i - 1][0]) >= 0:
                draw.line(poly[i - 1] + poly[i], fill=(150, 150, 200)) # (L-P) x (M-L) = C x B
            else:                                                      #  -2 - P  x  -1 - -2
                draw.line(poly[i - 1] + poly[i], fill=(200, 80, 80))
            draw.text(poly[i], str(i), fill=(130, 130, 130))
    draw.line((player[0] - 3, player[1] - 3, player[0] + 3, player[1] + 3), fill=(255, 0, 0))
    draw.line((player[0] - 3, player[1] + 3, player[0] + 3, player[1] - 3), fill=(255, 0, 0))
    img.save(open('out.png', 'wb'), 'PNG')

sm = simpleMaze()
show(sm, (200 - 9, 200 - 11), 420, 420)

os.system('out.png')

