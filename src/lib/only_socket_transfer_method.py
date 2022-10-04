from .message import Message
from .UDPHandler import recv, send


class OnlySocketTransferMethod:
    def __init__(self, messageSocket):
        self.messageSocket = messageSocket

    def recvMessage(self, timeout):
        self.messageSocket.settimeout(timeout)
        bit, data, address = recv(self.messageSocket)
        return Message(data, address, bit)

    def sendMessage(self, bit, data, address):
        send(self.messageSocket, bit, data, address)
