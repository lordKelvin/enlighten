from winterstone import WinterPlugin

class Dummy(WinterPlugin):
    def activate(self):
        self.api.info('%s: start' % self.name)