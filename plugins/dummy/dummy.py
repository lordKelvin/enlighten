from winterstone import WinterPlugin

class Dummy(WinterPlugin):
    def activate(self):
        self.api.info('%s: start' % self.name)
        return WinterPlugin.activate(self)

    def deactivate(self):
        self.api.info('%s: stop' % self.name)
        return WinterPlugin.deactivate(self)