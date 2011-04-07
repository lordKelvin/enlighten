# -*- coding: utf-8 -*-
from datetime import datetime
import os
import re
import sys
from snowflake import *

from PyQt4.QtGui import *
from PyQt4 import uic
from PyQt4.QtCore import *

starttime = datetime.now()

cwd = sys.path[0] + '/'
icons = loadIcons(cwd+'icons/')

from winterstone import WinterObject, WinterApp, WinterAPI, WinterGUI, WinterMainApp, WinterPM, WinterPlugin


class API(WinterAPI):
    def setText(self, *args, **kwargs):
        self.ex('setText')(*args, **kwargs)

    def echo(self, *args, **kwargs):
        self.ex('echo')(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.ex('info')(*args, **kwargs)

    def debug(self, *args, **kwargs):
        self.ex('debug')(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.ex('error')(*args, **kwargs)

    def info(self, msg):
        self.app.info(msg)


class WinterQtApp(QMainWindow, WinterApp):
    __apiclass__ = API

    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi(cwd + "main.ui", self)
        self.afterMWInit()
        WinterApp.__init__(self)
        self.api.app = self
        self.api.ex = self.__getitem__

        self.connect(self.debugLine, SIGNAL("textChanged(QString)"), self.newchar)
        self.connect(self.debugLine, SIGNAL("returnPressed()"), self.command)

        screen = QDesktopWidget().screenGeometry()
        QMainWindow.setGeometry(self, 0, 0, screen.width(), screen.height())

        self.setWindowTitle(self.config.info['title'])
        self.setWindowIcon(QIcon(icons['app']))
        self.dockWidget.hide()
        self.statusbar.showMessage('Done')
        self.toolBar.setIconSize(QSize(int(self.config.options['tbicon_size']),int(self.config.options['tbicon_size'])))
        self.toolBar.setMovable(False)

        self.addToolButton('restart','core','regen_maze')


        self.core.main()


    def afterMWInit(self):
        pass


    def getMethod(self, module, key):
        try:
            if module=='core':
                return eval('self.core.%s' % key)
            else:
                return eval('self.%s' % key)
        except:
            return False

    def __getitem__(self, key):
        return self.getMethod('main', key)

    def newchar(self):
        ln = re.findall('[^ ]*', str(self.debugLine.text()))[0]
        module = re.findall('([^ ]*)\.', str(self.debugLine.text()))
        if module:
            module = module[0]
            ln = ln.replace(module + '.', '')
        if self.getMethod('main', ln):
            self.color = QColor(0, 150, 0)
            self.decor = 'underline'
            self.dlock = False
        elif self.getMethod(module, ln):
            self.color = QColor(0, 150, 0)
            self.decor = 'underline'
            self.dlock = False
        else:
            self.color = QColor(140, 0, 0)
            self.decor = 'none'
            self.dlock = True
            #            self.color = QtGui.QColor(30, 144, 255)
        self.debugLine.setStyleSheet(
                "QWidget { font: bold; color: %s; text-decoration: %s;}" % (self.color.name(), self.decor))

    def command(self):
        if not self.dlock:
            line = re.findall('[^ ]*', str(self.debugLine.text()))
            ln = line[0]
            module = re.findall('([^ ]*)\.', str(self.debugLine.text()))
            if module:
                module = module[0]
                ln = ln.replace(module + '.', '')
            else:
                module = 'main'
            args = line[1:]
            for arg in args:
                if not arg:
                    args.remove(arg)
            try:
                self.getMethod(module, ln)(*args)
                self.debugLine.clear()
            except Exception, e:
                self['error'](str(e))


    def makeMessage(self, msg, color='', icon='', bold=True, fgcolor='', ts=False):
        if ts:
            timestamp = datetime.now().strftime('%H:%M:%S')
            item = QListWidgetItem('[%s] %s' % (timestamp, msg))
        else:
            item = QListWidgetItem(msg)
        if 'listitem_bgcolor' in self.config.options and not color:
        #            color=self.config.options['listitem_bgcolor']
            if color:
                item.setBackground(QColor(color))
        if 'listitem_font' in self.config.options:
            font = QFont(self.config.options['listitem_font'])
        else:
            font = QFont('Sans')
        font.setBold(bold)
        font.setPointSize(int(self.config.options['font_size']))
        item.setFont(font)
        if not fgcolor and 'listitem_fgcolor' in self.config.options:
            fgcolor = self.config.options['listitem_fgcolor']
        item.setTextColor(QColor(fgcolor))
        if icon:
            item.setIcon(QIcon(icons[icon]))
        return item

    def info(self, msg):
        self.debugList.addItem(self.makeMessage(msg, 'lightgreen', 'ok', ts=True, fgcolor='black'))

    def error(self, msg, obj=''):
        if not obj:
            self.debugList.addItem(self.makeMessage(msg, 'red', 'error', ts=True, fgcolor='black'))
        else:
            self.debugList.addItem(self.makeMessage('%s::%s' % (obj, msg), 'red', 'error', ts=True, fgcolor='black'))

    def debug(self, msg):
        self.debugList.addItem(self.makeMessage(msg, 'lightyellow', 'warning', ts=True, fgcolor='black'))



    def addToolButton(self,icon,plugin,method):
        tb=QToolButton()
        tb.setIcon(QIcon(icons[icon]))
        self.toolBar.addWidget(tb)
        self.connect(tb, SIGNAL("clicked()"), self.getMethod(plugin,method))
        return tb