

import RSS_Manager
import abc
from database import DatabaseManagement

class Subject:
    """
    Know its observers. Any number of Observer objects may observe a
    subject.
    Send a notification to its observers when its state changes.
    """

    def __init__(self):
        self._observers = set()
        self.rsslink = None

    def attach(self, observer):
        observer._subject = self
        self._observers.add(observer)

    def detach(self, observer):
        observer._subject = None
        self._observers.discard(observer)

    def _notify(self):
        for observer in self._observers:
            observer.update(self.rsslink)

    @property
    def newrsslink(self):
        return self.rsslink

    @newrsslink.setter
    def newrsslink(self, arg):
        self.rsslink = arg
        self._notify()

class Observer(metaclass=abc.ABCMeta):
    """
    Define an updating interface for objects that should be notified of
    changes in a subject.
    """

    def __init__(self):
        self._subject = None
        self._observer_state = None

    @abc.abstractmethod
    def update(self, arg):
        pass

class rsslinksobserver(Observer):

    def update(self, args):
        self._subject = args
        with DatabaseManagement.datalink('rssdata','rsslinks') as datalinker:
            for document in datalinker.find({}):
                print(document)




if __name__ == "__main__":
    sub = Subject()
    obs = rsslinksobserver()
    sub.attach(obs)
    sub.newrsslink = 'test'