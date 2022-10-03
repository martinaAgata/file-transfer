from .UDPHandler import send


class ClientHandlerTransferMethod:

    def __init__(self, messageSocket, messageQueue):
        self.messageSocket = messageSocket
        self.messageQueue = messageQueue

    def recvMessage(self, timeout):
        return self.messageQueue.get(timeout=timeout)

    def sendMessage(self, bit, data, address):
        send(self.messageSocket, bit, data, address)
