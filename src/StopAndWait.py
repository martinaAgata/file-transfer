import logging
from UDPHandler import recv, send, BUFSIZE

class StopAndWait:
    def __init__(self, socket):
        self.socket = socket
        self.bit = 0

    def alternateBit(self):
        if self.bit == 0:
            self.bit = 1
        else:
            self.bit = 0

    def is_ack(self, message):
        splited_message = message.decode().split(" ", 1)
        status = splited_message[0]

        response = ''
        if len(splited_message) == 2:
            response = splited_message[1]

        if status == 'ACK':
            return (True, response)
        elif status == 'NAK':
            return (False, response)
        else:
            return (False, "Unknown acknowledge: " + message.decode())

    def checkDuplicateACK(self, bitRcv, data, port, serverIP):
        while bitRcv != self.bit:
            try:
                logging.debug(f"ACK repeated, do nothing and waiting for next ACK")
                bitRcv, message, serverAddress = recv(self.socket)
                logging.debug(f"Receiving ACK {bitRcv}, {message} from {serverAddress}")
            except Exception:
                logging.debug(f"Timeout waiting for not duplicated ACK, resending data")
                send(self.socket, self.bit, data, serverIP, port)

    def checkingACKException(self, message):
        (ack, response) = self.is_ack(message)
        if not ack:
            # TODO: Think a better error
            raise BaseException(response)

    def sendAndWaitForAck(self, data, serverIP, port=None):
        sent = False
        while not sent:
            try:
                send(self.socket, self.bit, data, serverIP, port)
                logging.debug(f"Sending data.")
                bitRcv, message, serverAddress = recv(self.socket)
                logging.debug(f"Receiving ACK {bitRcv}, {message} from {serverAddress}")

                self.checkDuplicateACK(bitRcv, data, port, serverIP)
                self.checkingACKException(message)

                sent = True
            except Exception:
                logging.debug(f"Timeout waiting for ACK, resending data")

    def recvCheckingDuplicates(self, bit=0):
        bitRcv, maybeFileContent, clientAddress = recv(self.socket)

        while bitRcv == bit:
            send(self.socket, bit, 'ACK'.encode(), clientAddress)
            bitRcv, maybeFileContent, clientAddress = recv(self.socket)

        return bitRcv, maybeFileContent, clientAddress

    def send_filename(self, command, filename, serverIP, port):
        self.sendAndWaitForAck((command + ' ' + filename).encode(), serverIP, port)
        self.alternateBit()

    def send_file(self, file, clientAddress, port=None):
        data = file.read(BUFSIZE)

        while data:
            logging.debug("Read data from file")
            self.sendAndWaitForAck(data, clientAddress, port)
            data = file.read(BUFSIZE)
            self.alternateBit()

    def recv_file(self, maybeFileContent, file, address, bit):
        while maybeFileContent != "END".encode():
            logging.debug(
                f"Received file content from {address}")

            # Write file content to new file
            file.write(maybeFileContent)
            logging.debug("File content written")

            # Send file content received ACK.
            send(self.socket, bit, 'ACK'.encode(), address)
            logging.debug(f"ACK sent to {address}")
            bit, maybeFileContent, clientAddress = self.recvCheckingDuplicates(bit)