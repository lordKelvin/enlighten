import os
import sys


cwd = sys.path[0] + '/'

def loadIcons(icondir, ext='.png'):
    icons = {}
    dirList = os.listdir(icondir)
    for fname in dirList:
        if fname.endswith(ext):
            icons[fname[:-4]] = str(icondir + fname)
    return icons