import gevent
from gevent.queue import Queue


class VendingMachine(gevent.Greenlet):

    def __init__(self):
        self.inbox = Queue()
        Greenlet.__init__(self)

    def _run(self):
        self.running = True

        while self.running:
            message = self.inbox.get()

