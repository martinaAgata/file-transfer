from .UDPHandler import send

class ClientHandlerTransferMethod:

    def __init__(self, messageSocket, messageQueue):
        self.messageSocket = messageSocket
        self.messageQueue = messageQueue

    def recvMessage(self, timeout):
        if timeout == 0:
            return self.messageQueue.get_nowait()
        return self.messageQueue.get(timeout=timeout)

    def sendMessage(self, bit, data, address):
        send(self.messageSocket, bit, data, address)