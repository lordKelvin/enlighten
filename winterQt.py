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


class SettingsManager(QMainWindow):
    def __init__(self, app, *args,**kwargs):
#        App.__init__(self,*args,**kwargs)
        QMainWindow.__init__(self)
        uic.loadUi(cwd+"sm.ui", self)
        self.connect(self.restartButton, SIGNAL("clicked()"), self.restart)

        self.app=app
        self.app.sm=self
        if self.app.config.options['plugins']:
            self.loadPlugins()
            self.connect(self.listWidget, SIGNAL("itemClicked(QListWidgetItem *)"), self.echoInfo)
            self.connect(self.listWidget, SIGNAL("itemChanged(QListWidgetItem *)"), self.togglePlugin)
        else:
            self.tabWidget.removeTab(1) #tabPlugins
            self.tabWidget.removeTab(1) #tabPlugins config.options

        self.loadSettings()
        self.connect(self.applyButton, SIGNAL("clicked()"), self.applyOptions)

    def loadSettings(self):
        self.opts={}
        self.opts.update(self.app.config.options)
        if self.app.config.options.plugins:
            self.popts=self.app.project.config['Plugins'].copy()
        self.fill(self.opts,self.tableWidget)
        if self.app.config.options.plugins:
            self.fill(self.popts,self.tableWidget_2)

        self.connect(self.tableWidget, SIGNAL("itemChanged(QTableWidgetItem *)"), self.changeOption)
        self.connect(self.tableWidget_2, SIGNAL("itemChanged(QTableWidgetItem *)"), self.changeOption)

    def fill(self,array,widget):
        row=0
        for var in array:
            if not var.endswith('_desc') and var!='activated':
                widget.insertRow(row)
                widget.setVerticalHeaderItem(row,QTableWidgetItem(var))
                vitem=QTableWidgetItem(str(array[var]))
                vitem.name=var
                if array[var] in [True,False]:
                    vitem.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled ))
                    check = Qt.Checked if array[var]=='True' else Qt.Unchecked
                    vitem.setCheckState(check)
                widget.setItem(row,0,vitem)
                if '%s_desc' % var in array:
                    desc=array['%s_desc' % var]
                else:
                    desc=''
                ditem=QTableWidgetItem(desc)
                ditem.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled ))
                widget.setItem(row,1,ditem)
                row+=1

    def loadPlugins(self):
        for plugin in self.app.pm.getAllPlugins():
            item = QListWidgetItem(plugin.name)
            item.plugin=plugin
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

            check = Qt.Checked if plugin.plugin_object.is_activated else Qt.Unchecked

            item.setCheckState(check)
            self.listWidget.addItem(item)

    def applyOptions(self):
        self.app.config.options=self.opts
#        if self.app.config.options.plugins:
#            self.app.project.config['Plugins']=self.popts
        self.app.saveConfig()
        self.close()

    def restart(self):
        self.applyOptions()
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def changeOption(self,item): #!!!!!!!!!!!!!!!!! int save
        if item.checkState()==2 or (not item.checkState() and item.text() in ['False','True']):
            text = 'True' if item.checkState() else 'False'
            item.setText(text)
        if item.name in self.opts:
            value=item.text().__str__().encode('cp1251')
            if value in ['True','False']:
                self.opts[item.name]=eval(value)
            else:
                self.opts[item.name]=value
        else:
            self.popts[item.name]=item.text()
        self.statusBar.showMessage('%s change to %s' % (item.name,item.text()))

    def echoInfo(self,item):
        info=self.getInfo(item.plugin)
        self.plainTextEdit.setPlainText(QString(info))

    def togglePlugin(self,item):
        state=item.checkState()
        if state:
            self.app.activate(item.plugin.name,permanent=True)
        else:
            self.app.deactivate(item.plugin.name,permanent=True)

        check = Qt.Checked if item.plugin.name in self.app.pm.active else Qt.Unchecked
        item.setCheckState(check)
        if check == Qt.Checked:
            self.statusBar.showMessage('%s activated' % item.plugin.name)
        else:
            self.statusBar.showMessage('%s deactivated' % item.plugin.name)

    def getInfo(self,pi):
        return 'Name: %s\n \
        Description: %s\n \
        Author: %s\n \
        Version: %s\n \
        Category: %s\n \
        State: %s\n \
        ' % (pi.name, pi.description, pi.author, pi.version, pi.category, pi.state)



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
        self.addToolButton('warning','main','toggleDebug')

        self.addToolButton('restart','core','regen_maze')


        self.core.main()

        self.sm=SettingsManager(self)
        self.smTB=QToolButton()
        self.smTB.setIcon(QIcon(icons['configure']))
        self.toolBar.addWidget(self.smTB)
        self.connect(self.smTB, SIGNAL("clicked()"), self.sm.show)
        self.api.info('Application initialised')
        
    def toggleDebug(self):
        if self.dockWidget.isHidden():
            self.dockWidget.show()
        else:
            self.dockWidget.hide()

    def afterMWInit(self):
        pass


    def getMethod(self, module, key):
        try:
            if module=='core':
                return eval('self.core.%s' % key)
            else:
                return eval('self.%s' % key)
        except Exception, e:
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
        method=self.getMethod(plugin,method)
        print method
        self.connect(tb, SIGNAL("clicked()"), method)
        return tb