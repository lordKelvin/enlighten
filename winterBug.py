# -*- coding: utf-8 -*-
from datetime import datetime
import re
import inspect
from snowflake import *

from config import Config
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class try_this(object):
    def __init__(self, api):
        self.api=api

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            try:
                return f(*args,**kwargs)
            except Exception,e:
                self.api.error(e)
        return wrapped_f

class WinterQtDebug(QDockWidget):

    class WinterLine(QLineEdit):
        def __init__(self, parent):
            QLineEdit.__init__(self)
            self.app=parent.app
            self.parent=parent
            self.connect(self, SIGNAL("textChanged(QString)"), self._newchar)
            self.connect(self, SIGNAL("returnPressed()"), self._command)
            self.defaults = dir(self.parent.app)
            self.completerList = QStringList()
            for i in self.defaults:
                self.completerList.append(QString(i))
            lineEditCompleter = QCompleter(self.completerList)
            lineEditCompleter.setCompletionMode(QCompleter.InlineCompletion)
            lineEditCompleter.setCaseSensitivity(Qt.CaseInsensitive)
            self.setCompleter(lineEditCompleter)

        def _newchar(self):
            ln = re.findall('[^ ]*', str(self.text()))[0]
            if self.app.getMethod(ln):
                self.color = QColor(0, 150, 0)
                self.decor = 'underline'
                self.dlock = False
            else:
                self.color = QColor(140, 0, 0)
                self.decor = 'none'
                self.dlock = True
            self.setStyleSheet(
                    "QWidget { font: bold; color: %s; text-decoration: %s;}" % (self.color.name(), self.decor))

        def _command(self):
            if not self.dlock:
                line = re.findall('[^ ]*', str(self.text()))
                ln = line[0]
                module = re.findall('([^ ]*)\.', str(self.text()))
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
                    self.app.getMethod(ln)(*args)
                    self.clear()
                except Exception, e:
                    self.parent.error(str(e))

    class WinterErrorList(QListWidget):
        def __init__(self,parent):
            QListWidget.__init__(self)
            self.parent=parent

        def addItem(self, item, *args,**kwargs):
            QListWidget.addItem(self,item)
            bt=self.addItemButton(item,'help',self.parent.inspectE)

        def addItemButton(self,item,icon,method):
            widget=QWidget(self)
            bt=QPushButton(QIcon(self.parent.api.icons[icon]),'')
            bt.setBaseSize(QSize(14,14))
            bt.setIconSize(QSize(14,14))
#            bt.setFlat(True)
            bt.method=method
            bt.item=item
            bt.clicked.connect(self.sig_map)
            hb=QHBoxLayout(widget)
            hb.addSpacerItem(QSpacerItem(self.width(),0))
            widget.setLayout(hb)
            hb.insertWidget(1,bt)
            return bt

        def sig_map(self):
            try:
                self.sender().method(self.sender().item)
            except AttributeError:
                self.sender().method()

    def __init__(self,app):
        QDockWidget.__init__(self)
        f = file('%sconfig/debug.cfg' % cwd)
        self.config = Config(f)
        self.exceptions=[]
        self.app=app
        self.api=app.api
        widget=QTabWidget()
        log=QWidget()
        todo=QTextEdit()
        todo.setPlainText(getFileContent(cwd+'TODO'))
        todo.setReadOnly(True)
        self.errorList=self.WinterErrorList(self)
        widget.addTab(log,'Log')
        widget.addTab(self.errorList,'Errors')
        widget.addTab(todo,'ToDo')
        layout=QVBoxLayout(log)
        self.debugLine=self.WinterLine(self)
        self.debugList=QListWidget()
        layout.addWidget(self.debugLine)
        layout.addWidget(self.debugList)
        log.setLayout(layout)
        self.setWidget(widget)

        self.app.addDockWidget(Qt.BottomDockWidgetArea,self)
        self.hide()

    def inspectE(self,*args,**kwargs):
        self.app.dialog('warning','Error',str(self.sender().item.e))


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
            item.setIcon(QIcon(self.api.icons[icon]))
        return item

    def info(self, msg):
        self.debugList.addItem(self.makeMessage(msg, 'lightgreen', 'ok', ts=True, fgcolor='black'))

    def error(self, msg, obj=''):
        if not isinstance(msg,Exception):
            e=Exception(msg)
        else:
            e=msg
        self.exceptions.append(e)
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
#        print calframe[2][0]
#        print calframe[2][0].f_locals
        vmsg='%s\nMethod: %s; locals: %s' % (e,calframe[2][3],calframe[2][0].f_locals)
        if not obj:
            item=self.makeMessage(vmsg, 'red', 'error', ts=True, fgcolor='black')
            item2=self.makeMessage(msg, 'red', 'error', ts=True, fgcolor='black') #in qt you cant copy widget=((
        else:
            item=self.makeMessage('%s::%s' % (obj, vmsg), 'red', 'error', ts=True, fgcolor='black')
            item2=self.makeMessage('%s::%s' % (obj, msg), 'red', 'error', ts=True, fgcolor='black')
        item.e=e
        self.errorList.addItem(item)
        self.debugList.addItem(item2)

    def debug(self, msg):
        self.debugList.addItem(self.makeMessage(msg, 'lightyellow', 'warning', ts=True, fgcolor='black'))
