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

    def receive(self, address=None, lastSentMsg=None, lastSentBit=None, lastRcvBit=None, timeout=None):
        # TODO: change 5 to a constant
        for i in range(0, 5):
            try:
                # If it is a sender, we set a timeout, if not, recv is blocked until new message
                self.socket.settimeout(timeout)
                bit, data, address = recv(self.socket)

                # If it's the first message, then None is set, so the while condition is always false
                while lastRcvBit == bit:
                    logging.debug(f"Duplicated package with bit = {bit} and {data[:15]}")
                    # The recv sends another ACK msg, but the sender do nothing
                    if not timeout:
                        send(self.socket, bit, lastSentMsg, address)
                    self.socket.settimeout(timeout)
                    bit, data, address = recv(self.socket)
                return bit, data, address
            except Exception:
                # When sender throw a timeout exception, we re-send the message, at least until <CONSTANT> times
                logging.debug(f"Socket raise timeout exception while waiting for receiving message.")
                send(self.socket, lastSentBit, lastSentMsg, address)

        self.socket.settimeout(timeout)
        bit, data, address = recv(self.socket)

        # If it's the first message, then None is set, so the while condition is always false
        while lastRcvBit == bit:
            logging.debug(f"Duplicated package with bit = {bit} and {data[:15]}")
            # The recv sends another ACK msg, but the sender do nothing
            if not timeout:
                send(self.socket, bit, lastSentMsg, address)
            self.socket.settimeout(timeout)
            bit, data, address = recv(self.socket)
        return bit, data, address

    def send_file(self, file, address, timeout):
        try:
            data = file.read(BUFSIZE)

            while data:
                logging.debug("Read data from file")
                send(self.socket, self.bit, data, address)
                _, message, _ = self.receive(address, lastSentMsg=data, lastSentBit=self.bit,
                                             timeout=timeout)
                self.alternateBit()
                if message != "ACK".encode():
                    if message == "FIN".encode():
                        logging.info(f"FIN messsage received.")
                        send(self.socket, self.bit, "FIN_ACK".encode(), address)
                    else:
                        logging.error(f"Unknown message received {message.decode()}")
                        send(self.socket, self.bit, "FIN".encode(), address)
                    return
                data = file.read(BUFSIZE)
            # TODO: FIX THIS BUG! Think about what we have to do if END is never received
            send(self.socket, self.bit, "FIN".encode(), address)
            _, message, _ = self.receive(address, lastSentMsg="FIN".encode(), lastSentBit=self.bit,
                                         timeout=timeout)
            logging.debug("Sent FIN")
            logging.info("File transfer completed")
        except BaseException as err:
            logging.error(
                f"An error occurred when sending file: {format(err)}")

    def recv_file(self, file, address, lastSentMsg=None, lastRcvBit=None):
        lastBit, maybeFileContent, address = self.receive(address, lastSentMsg=lastSentMsg, lastRcvBit=lastRcvBit)

        while maybeFileContent != "FIN".encode():
            logging.debug(
                f"Received file content from {address}")

            # Write file content to new file
            file.write(maybeFileContent)
            logging.debug("File content written")

            # Send file content received ACK.
            send(self.socket, lastBit, 'ACK'.encode(), address)
            logging.debug(f"ACK sent to {address}")
            lastBit, maybeFileContent, address = self.receive(address, lastSentMsg='ACK'.encode(),
                                                                     lastRcvBit=lastBit)
        send(self.socket, lastBit, 'FIN_ACK'.encode(), address)
        logging.debug(f"FIN_ACK sent to {address}")
        logging.info(f"Received file from {address}")
