import threading as thr

from .definitions import TIMEOUT
from .utils import handle_action


class ClientHandler:
    """
    Client thread interface
    """

    def __init__(self, messageQueue, transfer_protocol, address, socket, dirpath):
        """
        Creates a Client Handler and initializes its initial attributes.
        """
        self.queue = messageQueue

        self.address = address
        self.socket = socket
        self.thread = thr.Thread(
            target=handle_action, args=(address, transfer_protocol, dirpath)
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
