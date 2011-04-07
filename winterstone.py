# -*- coding: utf-8 -*-
from _collections import defaultdict
import os
import types
import weakref
from config import Config, ConfigMerger

#from PySide import QtGui, QtCore, QtUiTools
#from PySide.QtGui import QMainWindow, QPushButton, QApplication
import imp

class WinterManager(object):
    '''
        Django ORM -like manager for WinterObject subclasses
    '''

    def __init__(self, cls):
        self.cls = cls

    def all(self):
        '''
            Use native object _get_all method
        '''
        return self.cls._get_all()

    def filter(self, **kwargs):
        '''
            Filter criteria pass like attr = value
            TODO: __api
        '''
        result = []
        for o in self.all():
            n = 0
            for crit in kwargs:
                try:
                    if o[crit] == kwargs[crit]:
                        n += 1
                except KeyError:
                    pass
            if n == len(kwargs):
                result.append(o)
        return result

    def get(self, **kwargs):
        '''
            Get only first item of filter. Without Django-like exeption about not-uniq item
        '''
        return self.filter(**kwargs)[0]

    def __getitem__(self, key):
        return self.cls._get_all()[key]


class WinterObject(object):
    '''
        Enhanced primitive object
    '''
    __refs__ = defaultdict(list)
    __manager__ = WinterManager

    def __init__(self):
        '''
            Some preparations for objectmanager
        '''
        self.__refs__[self.__class__].append(weakref.ref(self))
        self.__class__.objects = self.__class__.__manager__(self.__class__)

    @classmethod
    def _get_all(cls):
        '''
            Get all objects of this class
        '''
        lst = []
        for inst_ref in cls.__refs__[cls]:
            inst = inst_ref()
            if inst is not None:
                lst.append(inst)
        return lst


    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __call__(self, *args, **kwargs):
        pass

    def info(self, spacing=30, collapse=1):
        '''
            Print some debug information
        '''
        methodList = [e for e in dir(self) if callable(getattr(self, e))]
        processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
        print "\n".join(
                ["%s %s" % (method.ljust(spacing), processFunc(str(getattr(self, method).__doc__))) for method in
                 methodList])
        print '__dict__ =', self.__dict__

class Borg:
    '''
        Simple monostate class
    '''
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state

class WinterAPI(Borg):
    '''
        IO API for plugins
    '''

    def __init__(self):
        Borg.__init__(self)
        self.icons = {}
        icondir = 'icons'
        ext = '.png'
        dirList = os.listdir(icondir)
        for fname in dirList:
            if fname.endswith(ext):
                self.icons[fname[:-4]] = str(icondir + fname)

    def info(self, msg): pass

    def debug(self, msg): pass

    def error(self, msg): pass


class WinterPM(object):
    '''
        Plugin manager
    '''

    def findModules(self):
        '''
            Search plugin files
            http://wiki.python.org/moin/ModulesAsPlugins
        '''
        modules = set()
        for dir in os.listdir('plugins'):
            for filename in os.listdir('plugins/' + dir):
                module = None
                if filename.endswith(".py"):
                    module = filename[:-3]
                elif filename.endswith(".pyc"):
                    module = filename[:-4]
                if module is not None:
                    modules.add(module)
        return list(modules)

    def loadModule(self, name, path="plugins/"):
        """
            Return a named module found in a given path.
            http://wiki.python.org/moin/ModulesAsPlugins
        """
        (file, pathname, description) = imp.find_module(name, [path + name])
        return imp.load_module(name, file, pathname, description)

    def processPlugin(self, module):
        '''
            Create plugin instance from module
        '''
        for obj in module.__dict__.values():
            try:
                if issubclass(obj, WinterPlugin) and obj is not WinterPlugin:
                    plugin = obj()
                    plugin.name = module.__name__
                    try:
                        plugin.onLoad()
                        return plugin
                    except Exception, e:
                        return
            except:
                return


    def activateAll(self):
        for plugin in self.plugins:
            try:
                plugin.activate()
                plugin.active = True
            except Exception, e:
                plugin.active = False
                plugin.error = e


    def __init__(self):
        self.api = API()
        self.modules = [self.loadModule(name) for name in self.findModules()]
        self.plugins = [self.processPlugin(module) for module in self.modules]

class WinterPlugin(WinterObject):
    '''
        Base plugin class
    '''

    def __init__(self):
        self.api = API()
        WinterObject.__init__(self)
        WinterObject.__refs__[WinterPlugin].append(weakref.ref(self))

    def onLoad(self):
        '''
            Some base actions after create instance
        '''
        f = file('plugins/%s/plugin.cfg' % self.name)
        self.config = Config(f)

    def activate(self):
        '''
            Overload...able method for activate
        '''
        pass


class WinterApp(object):
    '''
        Main non-gui application class
    '''
    __apiclass__ = WinterAPI
    __pmclass__ = WinterPM

    def getMethod(self, module, key):
        if not key.startswith('_'):
            try:
                if module == 'core':
                    return eval('self.core.%s' % key)
                else:
                    return eval('self.%s' % key)
            except Exception, e:
                pass
        return False

    def __getitem__(self, key):
        return self.getMethod('main', key)

    def loadConfigs(self):
        self.config = ''
        self.configFiles = ['config/main.cfg', 'config/plugins.cfg']
        self.configs = []
        merger = ConfigMerger()
        for cf in self.configFiles:
            f = file(cf)
            temp = Config(f)
            self.configs.append(temp)
            if self.config:
                merger.merge(self.config, temp)
            else:
                self.config = temp

    def saveConfig(self):
        for i, cfg in enumerate(self.configs):
            f = file(self.configFiles[i], 'w')
            cfg.save(f)

    def __init__(self):
        self.api = self.__class__.__apiclass__()
        global API
        API = self.__class__.__apiclass__
        self.loadConfigs()
        from core import Core

        self.core = Core()
        self.core.app = self
        self.core.afterInit()
        if self.config.options.plugins:
            WinterPlugin()
            self.pm = self.__class__.__pmclass__()
            self.pm.activateAll()
        self.refreshMethods()

    def refreshMethods(self):
        self.methods = []
        for m in dir(self):
            if m.startswith('p_'):
                self.methods.append({'method': eval('self.core.%s' % m), 'sign': m.replace('p_', '')})
                #        print self.methods
        self.api.__dict__.update(self.methods)

        #        print dir(self.api)

#        print self.api.__dict__
'''
class WinterGUI(QMainWindow):
    def __init__(self, uiPath):
    #        pass
        QMainWindow.__init__(self)
        uiFile = QtCore.QFile(uiPath)
        uiFile.open(QtCore.QFile.ReadOnly)
        self.loader = QtUiTools.QUiLoader()
        self.win = self.loader.load(uiFile, self)
        uiFile.close()

class WinterMainApp(WinterGUI, WinterApp):
    def __init__(self):
        WinterApp.__init__(self)
        WinterGUI.__init__(self, 'main.ui')


class WinterSM(WinterGUI):
    def __init__(self):
        WinterGUI.__init__(self, 'main.ui')
'''