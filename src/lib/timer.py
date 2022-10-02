import time
import threading as thr
from .definitions import GBN_BASE_PACKAGE_TIMEOUT

class TimerPackageResender:
    
    def __init__(self, transferMethod, queue, address):
        self.queue = queue
        self.transferMethod = transferMethod
        self.thread = thr.Thread(
            target=self.timer, args=(address)
        )
    
    def start(self):
        self.thread.start()

    def stop(self):
        self.thread.join()

    def timer(self, address):
        time.sleep(GBN_BASE_PACKAGE_TIMEOUT)
        for (bit, data) in list(self.queue):
            self.transferMethod.sendMessage(bit, data, address)
        self.stop()