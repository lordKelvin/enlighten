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

    def echo(self, *args, **kwargs):
        self.ex('echo')(*args, **kwargs)


    def info(self, *args, **kwargs):
        if hasattr(self,'debugger'):
            self.debugger.info(*args, **kwargs)
        else:
            self.echo(*args,**kwargs)

    def debug(self, *args, **kwargs):
        if hasattr(self,'debugger'):
            self.debugger.debug(*args, **kwargs)
        else:
            self.echo(*args,**kwargs)

    def error(self, *args, **kwargs):
        if hasattr(self,'debugger'):
            self.debugger.error(*args, **kwargs)
        else:
            self.echo(*args,**kwargs)




class SettingsManager(QMainWindow):
    #TODO: plugins settings, list of plugins, array settings

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


    class settingsTable(QTableWidget):

        def fill(self,conf,conf_file,parent):
            self.parent=parent
            self.parent.configs.append(self)
            self.conf=conf
            self.conf_dict=conf.options
            self.conf_file=conf_file
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
            self.setSizePolicy(sizePolicy)
            self.setMaximumSize(QSize(16777215, 16777215))
            self.setAutoFillBackground(True)
            self.setColumnCount(2)
            self.setRowCount(0)
            item = QTableWidgetItem()
            self.setHorizontalHeaderItem(0, item)
            item = QTableWidgetItem()
            self.setHorizontalHeaderItem(1, item)
            self.horizontalHeader().setDefaultSectionSize(200)
            self.horizontalHeader().setStretchLastSection(True)
            self.verticalHeader().setStretchLastSection(False)
#            self.verticalLayout_2.addWidget(self)


            self.connect(self, SIGNAL("itemChanged(QTableWidgetItem *)"), self.changeOption)

            self.delegate = self.parent.myDelegate(self)
            self.setItemDelegateForColumn(0,self.delegate)
            row = 0
            self.items=[]
            array=self.conf_dict
            for var in array:
                if not var.endswith('_desc') and var != 'activated' and not var.endswith('_variants'):
                    self.insertRow(row)
                    self.setVerticalHeaderItem(row, QTableWidgetItem(var))
                    vitem = QTableWidgetItem(str(array[var]))
                    vitem.name = var
                    self.items.append(vitem)
                    if array[var] in [True, False]:
                        vitem.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled))
                        check = Qt.Checked if array[var] else Qt.Unchecked
                        vitem.setCheckState(check)
                    self.setItem(row, 0, vitem)
                    if '%s_desc' % var in array:
                        desc = array['%s_desc' % var]
                    else:
                        desc = ''
                    if '%s_variants' % var in array:
                        vitem.variants=array['%s_variants' % var]
                    ditem = QTableWidgetItem(desc)
                    ditem.name='ditem'
                    ditem.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled))
                    self.setItem(row, 1, ditem)
                    row += 1

        def changeOption(self, item):
            if item.checkState() == 2 or (not item.checkState() and item.text() in ['False', 'True']):
                text = 'True' if item.checkState() else 'False'
                item.setText(text)
            value = item.text().__str__().encode('cp1251')
            if item.name in self.conf_dict:
                if value in ['True', 'False']:
                    self.conf_dict[item.name] = eval(value)
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                    self.conf_dict[item.name] = value
                self.parent.statusBar.showMessage('%s change to %s' % (item.name, item.text()))

        def save(self):
            f = file(self.conf_file, 'w')
            self.conf.save(f)

    def __init__(self, app, *args, **kwargs):
        QMainWindow.__init__(self)
        self.resize(746, 545)
        self.centralwidget = QWidget(self)
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setTabPosition(QTabWidget.West)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tab_2 = QWidget()
        self.verticalLayout_2 = QVBoxLayout(self.tab_2)

        self.verticalLayout_3.addWidget(self.tabWidget)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QPushButton('Cancel',self.centralwidget)
        self.horizontalLayout.addWidget(self.cancelButton)
        self.restartButton = QPushButton('Apply and Restart',self.centralwidget)
        self.horizontalLayout.addWidget(self.restartButton)
        self.applyButton = QPushButton('Apply',self.centralwidget)
        self.horizontalLayout.addWidget(self.applyButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.setCentralWidget(self.centralwidget)
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        self.app = app
        self.app.sm = self
        self.configs=[]

        self.tableWidget=self.settingsTable()
        self.tableWidget.fill(self.app.config,cwd+'config/main.cfg',self)
        self.sttab=self.tabWidget.addTab(self.tableWidget,'Settings')


        if self.app.config.options.debug:
            self.dbgTable=self.settingsTable(self.tabWidget)
            self.dbgTable.fill(self.app.debugger.config,cwd+'config/debug.cfg',self)
            self.dbgtab=self.tabWidget.addTab(self.dbgTable,'Debug')

        if self.app.config.options.plugins:
            self.tabPlugins = QWidget()
            self.verticalLayout = QVBoxLayout(self.tabPlugins)
            self.listWidget = QListWidget(self.tabPlugins)
            self.verticalLayout.addWidget(self.listWidget)
            self.plainTextEdit = QPlainTextEdit(self.tabPlugins)
            self.verticalLayout.addWidget(self.plainTextEdit)
            self.tabWidget.addTab(self.tabPlugins, 'Plugins')
            self.loadPlugins()
            self.connect(self.listWidget, SIGNAL("itemClicked(QListWidgetItem *)"), self.echoInfo)
            self.connect(self.listWidget, SIGNAL("itemChanged(QListWidgetItem *)"), self.togglePlugin)


        self.connect(self.restartButton, SIGNAL("clicked()"), self.restart)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self.close)
        self.connect(self.applyButton, SIGNAL("clicked()"), self.applyOptions)
#        self.onnect(self.tableWidget_2, SIGNAL("itemChanged(QTableWidgetItem *)"), self.changeOption)



    def loadPlugins(self):
        for plugin in self.app.pm.plugins:
            item = QListWidgetItem(plugin.name)
            item.plugin = plugin
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

            check = Qt.Checked if plugin.active else Qt.Unchecked

            item.setCheckState(check)
            self.listWidget.addItem(item)

    def applyOptions(self):
        for cfg in self.configs:
            cfg.save()
        if self.app.config.options.plugins:
            self.savePlugins()
        self.close()

    def restart(self):
        self.applyOptions()
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def echoInfo(self, item):
        info = self.getInfo(item.plugin)
        self.plainTextEdit.setPlainText(QString(info))

    def togglePlugin(self, item):
        state = item.checkState()
        if state:
            self.app.pm.activate(item.plugin)
        else:
            self.app.pm.deactivate(item.plugin)

        check = Qt.Checked if item.plugin.active else Qt.Unchecked
        item.setCheckState(check)
        if check == Qt.Checked:
            self.statusBar.showMessage('%s activated' % item.plugin.name)
        else:
            self.statusBar.showMessage('%s deactivated' % item.plugin.name)

    def savePlugins(self):
        names=[]
        for p in self.app.pm.plugins:
            names.append(p.name)
        self.app.p_config.plugins.active=names
        f = file(cwd+'config/plugins.cfg','w')
        self.app.p_config.save(f)

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
        if self.config.options.debug:
            self.debugger=WinterQtDebug(self)
            self.api.debugger=self.debugger
            self.addToolButton('warning', 'main', 'toggleDebug')

        screen = QDesktopWidget().screenGeometry()
        QMainWindow.setGeometry(self, 0, 0, screen.width(), screen.height())

        self.setWindowTitle(self.config.info['title'])
        self.setWindowIcon(QIcon(self.api.icons['app']))
        self.statusbar.showMessage('Done')
        self.toolBar.setIconSize(
                QSize(int(self.config.options['tbicon_size']), int(self.config.options['tbicon_size'])))
        self.toolBar.setMovable(False)


        self.addToolButton('restart', 'core', 'regenMaze')

        self.core.main()


        if self.config.options.plugins:
            self.pm.activateAll()
            self.api.info('Plugins initialised')

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
        self.api.info(*args,**kwargs)

    def error(self,*args,**kwargs):
        self.api.error(*args,**kwargs)

    def debug(self,*args,**kwargs):
        self.api.debug(*args,**kwargs)

    def echo(self,*args, **kwargs):
        print args[0]

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