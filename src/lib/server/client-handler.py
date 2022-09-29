import threading as thr
import queue
from ..definitions import TIMEOUT
from ..utils import handle_action


class ClientHandler:
    """
    Document me please!
    """
    def __init__(self, address, socket, dirpath):
        """
        Creates a Client Handler and initializes its initial attributes.
        """
        self.queue = queue.Queue()
        self.address = address
        self.socket = socket
        self.thread = thr.Thread(
            target=handle_action,
            args=(address, socket, self.queue, dirpath)
        )

    def start_thread(self):
        """
        Spawns own thread
        """
        self.thread.start()

    def send(self, message):
        """
        Inserts message at own queue
        """
        self.queue.put(message)  # TODO: Full Exception.

    def join(self):
        """
        Waits for the thread to end
        """
        self.thread.join(TIMEOUT)
