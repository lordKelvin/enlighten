#!/usr/bin/env python
from PyQt4.uic.Compiler.qtproxies import QtCore
import os
from main import UI
from winterQt import API
from winterstone import WinterApp

__author__ = 'averrin'

#from avlib import logger, API, try_this, App, Project, cwd

from snowflake import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import sys



#TODO: plugin categories

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

    def changeOption(self,item):
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


def main():
#    print dir(logger)
    api=API()
    qtapp = QApplication(sys.argv)
    app=UI()
    sm=SettingsManager(app)
    sm.show()
    print 'after alert'
    qtapp.exec_()

if __name__ == '__main__':
    main()






