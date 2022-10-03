import logging
from .message import Message
from .definitions import (BUFSIZE, UPLOAD, DOWNLOAD, DATA,
                          FIN, FIN_ACK, ACK, NAK, TIMEOUT)


class StopAndWait:
    def __init__(self, transferMethod):
        self.bit = 0
        self.transferMethod = transferMethod

    def alternateBit(self):
        self.bit = 1 - self.bit

    # Returns a Message received (that is not duplicated) from the other part.
    def receive(self, address=None, lastSentMsg=None, lastSentBit=None, lastRcvBit=None, timeout=None):
        # TODO: change 5 to a constant
        for _ in range(0, 5):
            try:
                # If it is a sender, we set a timeout, if not, recv is blocked until new message

                message = self.transferMethod.recvMessage(timeout)

                # If it's the first message, then None is set, so the while condition is always false
                while lastRcvBit == message.bit:
                    logging.debug(
                        f"Duplicated package with bit = {message.bit} and {message.data[:15]}")
                    # The recv sends another ACK msg, but the sender do nothing
                    if not timeout:
                        self.transferMethod.sendMessage(
                            message.bit, lastSentMsg, address)

                    message = self.transferMethod.recvMessage(timeout)

                logging.debug(
                    f"Message received from {message.clientAddress} successfully")
                return message

            # Message retransmission in case of timeout
            except Exception as err:
                # When sender throw a timeout exception, we re-send the message, at least until <CONSTANT> times
                logging.debug(
                    f"Message queue raise timeout exception while waiting for receiving message: {format(err)}")
                self.transferMethod.sendMessage(
                    lastSentBit, lastSentMsg, address)

        # TODO: possible BUG. If a 6th timeout occurrs, then it is NOT catched and the application might close badly
        message = self.transferMethod.recvMessage(timeout)

        # If it's the first message, then None is set, so the while condition is always false
        while lastRcvBit == message.bit:
            logging.debug(
                f"Duplicated package with bit = {message.bit} and {message.data[:15]}")
            # The recv sends another ACK msg, but the sender do nothing
            if not timeout:
                self.transferMethod.sendMessage(
                    lastSentBit, lastSentMsg, address)

            message = self.transferMethod.recvMessage(timeout)

        logging.debug(
            f"Message received from {message.clientAddress} successfully")
        return message

    def send_file(self, file, address, timeout):

        # StopAndWait initialize bit in 0. We alternate it to 1 so the receiver maintains its bit in 0, so
        # receiver do not interpretate it as duplicate. It is hard to explain :(
        self.alternateBit()
        try:
            data = file.read(BUFSIZE)

            while data:
                logging.debug("Read data from file")

                self.transferMethod.sendMessage(self.bit, data, address)
                logging.debug(f"Sent data to {address}")

                # TODO: BUG no deberíamos pasarle al receive el lastRecvBit acá? porque así esperamos el
                # ACK correcto (nos puede llegar un ACK duplicado proveniente
                # de que le mandamos un duplicado al receiver por un timeout)
                message = self.receive(
                    address, lastSentMsg=data, lastSentBit=self.bit, timeout=timeout)
                self.alternateBit()

                if message.type != ACK:
                    if message.type == FIN:
                        logging.info(
                            f"{FIN} messsage received from {address}.")
                        self.transferMethod.sendMessage(
                            self.bit, FIN_ACK.encode(), address)
                        logging.debug(f"{FIN_ACK} messsage sent to {address}.")
                    else:
                        logging.error(
                            f"Unknown message received: {message.data[:15]}, from {address}")
                        self.transferMethod.sendMessage(
                            self.bit, FIN.encode(), address)
                        logging.info(f"{FIN} messsage sent to {address}.")
                    logging.error("File transfer NOT completed")
                    return

                data = file.read(BUFSIZE)

            # TODO: FIX THIS BUG! Think about what we have to do if END is never received

            self.transferMethod.sendMessage(self.bit, FIN.encode(), address)
            logging.info(f"{FIN} messsage sent to {address}.")

            _ = self.receive(address, lastSentMsg=FIN.encode(),
                             lastSentBit=self.bit, timeout=timeout)
            logging.info("File transfer completed")

        except Exception as err:
            logging.error(
                f"An error occurred when sending file: {format(err)}")

    def recv_file(self, file, address, lastSentMsg=None, lastRcvBit=None):
        message = self.receive(
            address, lastSentMsg=lastSentMsg, lastRcvBit=lastRcvBit)

        while message.type == DATA:
            logging.debug(
                f"Received file content from {message.clientAddress}")

            # Write file content to new file
            file.write(message.data)
            logging.debug("File content written")

            # Send file content received ACK.
            raw_message_to_send = ACK.encode()
            self.transferMethod.sendMessage(
                message.bit, raw_message_to_send, message.clientAddress)
            logging.debug(f"{ACK} sent to {message.clientAddress}")
            message = self.receive(message.clientAddress, lastSentMsg=raw_message_to_send,
                                   lastRcvBit=message.bit)

        if message.type == FIN:
            logging.info(
                f"{FIN} messsage received from {message.clientAddress}.")
            self.transferMethod.sendMessage(
                message.bit, FIN_ACK.encode(), message.clientAddress)
            logging.debug(
                f"{FIN_ACK} messsage sent to {message.clientAddress}.")
            logging.info(f"Received file from {message.clientAddress}")
        else:
            logging.error(
                f"Unknown message received {message.data[:15]} from {message.clientAddress}")
            self.transferMethod.sendMessage(
                message.bit, FIN.encode(), message.clientAddress)
            logging.debug(f"{FIN} messsage sent to {message.clientAddress}.")
            logging.info("File transfer NOT completed")
