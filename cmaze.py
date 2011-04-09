import random

size = 20
fullfill = 100
wallshort = 50

r = [[], []]
global h
m = []

def initrandom():
    for y in xrange(2, size, 2):
        for x in xrange(2, size, 2):
            r[0].append(x)
            r[1].append(y)
    global h
    h = len(r[0]) - 1

def getrandom(x, y):
    global h
    i = random.randrange(h)
    print x, y, ':)'
    x[0] = r[0][i]
    y[0] = r[1][i]
    r[0][i] = r[0].pop(h)
    r[1][i] = r[1].pop(h)
    h -= 1
    return h

def view():
    for y in xrange(size + 1):
        line = ''
        for x in xrange(size + 1):
            line += {0: '..', 1: 'XX'}[m[y][x]]
        print line

def main():
    for y in xrange(size + 1):
        tmp = []
        for x in xrange(size + 1):
            tmp.append(0)
        m.append(tmp)

    for i in xrange(size + 1):
        m[0][i] = 1
        m[size][i] = 1
        m[i][0] = 1
        m[i][size] = 1
    view()
    initrandom()
    startx = [0]
    starty = [0]
    while getrandom(startx, starty):
        if m[starty[0]][startx[0]] == 1:
            continue
        if random.randrange(100) > fullfill:
            continue

        [sx, sy] = {0: [1, 0], 1: [0, 1], 2: [-1, 0], 3: [0, -1]}[random.randrange(4)]

        while not m[starty[0]][startx[0]]:
            m[starty[0]][startx[0]] = 1
            if random.randrange(100) > wallshort:
                break
            startx[0] += sx
            starty[0] += sy
            m[starty[0]][startx[0]] = 1
            startx[0] += sx
            starty[0] += sy
    view()

main()
