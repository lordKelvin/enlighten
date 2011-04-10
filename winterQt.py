# -*- coding: utf-8 -*-
from datetime import datetime
from snowflake import *

from config import Config
from PyQt4.QtGui import *
from PyQt4 import uic
from PyQt4.QtCore import *
from winterstone import WinterApp, WinterAPI
from winterBug import *

starttime = datetime.now()



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


class myDelegate(QItemDelegate):
    def __init__(self, parent):
        QItemDelegate.__init__(self, parent)
        self.parent = parent
    def paint(self, painter, option, index):
        QItemDelegate.paint(self, painter, option, index)
    def createEditor(self, parent, option, index):
        value = index.model().data(index, Qt.EditRole).toString()
        item=self.parent.items[index.row()]
        try:
            value=int(value)
            editor = QSpinBox(parent)
        except ValueError:
            if hasattr(item,'variants'):
                editor = QComboBox(parent)
                editor.addItems(item.variants)
            else:
                editor = QLineEdit(parent)
        return editor
    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole).toString()
        item=self.parent.items[index.row()]
        try:
            editor.setText(value)
        except AttributeError:
            try:
                editor.setValue(int(value))
            except AttributeError:
                editor.setCurrentIndex(list(item.variants).index(value))
    def setModelData(self, editor, model, index):
        try:
            value = editor.text()
        except AttributeError:
            value = editor.currentText()
        model.setData(index, value, Qt.EditRole)
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class SettingsManager(QMainWindow):
    #TODO: plugins settings, list of plugins, array settings
    def __init__(self, app, *args, **kwargs):
        QMainWindow.__init__(self)
        uic.loadUi(cwd + "sm.ui", self)
        self.connect(self.restartButton, SIGNAL("clicked()"), self.restart)

        self.app = app
        self.app.sm = self
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
        self.opts = {}
        self.popts = {}
        self.opts.update(self.app.config.options)
        if self.app.config.options.plugins:
            self.popts.update(self.app.config.plugins) #LIE!!!!
        self.fill(self.opts, self.tableWidget)
        if self.app.config.options.plugins:
            self.fill(self.popts, self.tableWidget_2)

        self.connect(self.tableWidget, SIGNAL("itemChanged(QTableWidgetItem *)"), self.changeOption)
        self.connect(self.tableWidget_2, SIGNAL("itemChanged(QTableWidgetItem *)"), self.changeOption)

    def fill(self, array, widget):
        self.delegate = myDelegate(self)
        widget.setItemDelegateForColumn(0,self.delegate)
        row = 0
        self.items=[]
        for var in array:
            if not var.endswith('_desc') and var != 'activated' and not var.endswith('_variants'):
                widget.insertRow(row)
                widget.setVerticalHeaderItem(row, QTableWidgetItem(var))
                vitem = QTableWidgetItem(str(array[var]))
                vitem.name = var
                self.items.append(vitem)
                if array[var] in [True, False]:
                    vitem.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled))
                    check = Qt.Checked if array[var] else Qt.Unchecked
                    vitem.setCheckState(check)
                widget.setItem(row, 0, vitem)
                if '%s_desc' % var in array:
                    desc = array['%s_desc' % var]
                else:
                    desc = ''
                if '%s_variants' % var in array:
                    vitem.variants=array['%s_variants' % var]
                ditem = QTableWidgetItem(desc)
                ditem.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled))
                widget.setItem(row, 1, ditem)
                row += 1

    def loadPlugins(self):
        for plugin in self.app.pm.plugins:
            item = QListWidgetItem(plugin.name)
            item.plugin = plugin
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

            check = Qt.Checked if plugin.active else Qt.Unchecked

            item.setCheckState(check)
            self.listWidget.addItem(item)

    def applyOptions(self):
        self.app.config.options = self.opts
        #        if self.app.config.options.plugins:
        #            self.app.project.config['Plugins']=self.popts
        self.app.saveConfig()
        self.close()

    def restart(self):
        self.applyOptions()
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def changeOption(self, item):
        if item.checkState() == 2 or (not item.checkState() and item.text() in ['False', 'True']):
            text = 'True' if item.checkState() else 'False'
            item.setText(text)
        if item.name in self.opts:
            value = item.text().__str__().encode('cp1251')
            if value in ['True', 'False']:
                self.opts[item.name] = eval(value)
            else:
                try:
                    value = int(value)
                except ValueError:
                    pass
                self.opts[item.name] = value
        else:
            self.popts[item.name] = item.text()
        self.statusBar.showMessage('%s change to %s' % (item.name, item.text()))

    def echoInfo(self, item):
        info = self.getInfo(item.plugin)
        self.plainTextEdit.setPlainText(QString(info))

    def togglePlugin(self, item):
        state = item.checkState()
        if state:
            self.app.activate(item.plugin.name, permanent=True)
        else:
            self.app.deactivate(item.plugin.name, permanent=True)

        check = Qt.Checked if item.plugin.name in self.app.pm.active else Qt.Unchecked
        item.setCheckState(check)
        if check == Qt.Checked:
            self.statusBar.showMessage('%s activated' % item.plugin.name)
        else:
            self.statusBar.showMessage('%s deactivated' % item.plugin.name)

    def getInfo(self, pi):
        return 'Name: %s\n \
        Description: %s\n \
        Author: %s\n \
        Version: %s\n \
        State: %s\n \
        ' % (pi.name, pi.config.info.description, pi.config.info.author, pi.config.info.version, pi.state)

class WinterQtApp(QMainWindow, WinterApp):
    __apiclass__ = API

    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi(cwd + "main.ui", self)

        self._afterMWInit()
        WinterApp.__init__(self)
        self._afterAppInit()
        self.debugger=WinterQtDebug(self)

        screen = QDesktopWidget().screenGeometry()
        QMainWindow.setGeometry(self, 0, 0, screen.width(), screen.height())

        self.setWindowTitle(self.config.info['title'])
        self.setWindowIcon(QIcon(self.api.icons['app']))
        self.statusbar.showMessage('Done')
        self.toolBar.setIconSize(
                QSize(int(self.config.options['tbicon_size']), int(self.config.options['tbicon_size'])))
        self.toolBar.setMovable(False)
        self.addToolButton('warning', 'main', 'toggleDebug')

        self.addToolButton('restart', 'core', 'regenMaze')

        self.core.main()

        self.sm = SettingsManager(self)
        self.smTB = QToolButton()
        self.smTB.setIcon(QIcon.fromTheme('configure'))
        self.toolBar.addWidget(self.smTB)
        self.connect(self.smTB, SIGNAL("clicked()"), self.sm.show)
        self.api.info('Application initialised')

    def input(self,title='Input dialog',text='Please input'):
        input=''
        input=QInputDialog.getText(self,title,text)
        self['debug']('input value: %s' % input[0])
        return input[0]

    def dialog(self,type='info',title='Dialog',text='oops!!'):
        if type=='info':
            QMessageBox.information(self,title,text)
        elif type=='warning':
            QMessageBox.warning(self,title,text)
        elif type=='critical':
            QMessageBox.critical(self,title,text)
        elif type=='about':
            QMessageBox.about(self,title,text)

    def toggleDebug(self):
        if self.debugger.isHidden():
            self.debugger.show()
        else:
            self.debugger.hide()

    def _afterMWInit(self):
        pass

    def _afterAppInit(self):
        pass

    def info(self,*args,**kwargs):
        self.debugger.info(*args,**kwargs)

    def error(self,*args,**kwargs):
        self.debugger.error(*args,**kwargs)

    def debug(self,*args,**kwargs):
        self.debugger.debug(*args,**kwargs)

    def addToolButton(self, icon, module, method):
        tb = QToolButton()
        tb.setIcon(QIcon.fromTheme(icon,QIcon(self.api.icons[icon])))
        self.toolBar.addWidget(tb)
        method = self.getMethod(method, module)
        self.connect(tb, SIGNAL("clicked()"), method)
        return tb

    @try_this(API())
    def getMethod(self, key, module='main'):
        return WinterApp.getMethod(self,key,module)