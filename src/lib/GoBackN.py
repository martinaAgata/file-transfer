import logging
import queue
from .timer import RepeatingTimer
from .definitions import (BUFSIZE, GBN_BASE_PACKAGE_TIMEOUT, UPLOAD, DOWNLOAD, DATA,
                          FIN, FIN_ACK, ACK, NAK, TIMEOUT, GBN_RECEIVER_TIMEOUT)

def sendWindow(transferMethod, q, address):
    logging.debug("Timeout event occurred. Sending all packages from the queue.")
    for (bit, data) in list(q.queue):
        transferMethod.sendMessage(bit, data, address)

class GoBackN:
    def __init__(self, transferMethod):
        self.nextSeqNumber = 1
        self.base = 1
        self.windowSize = 2
        self.timer = None
        self.sentPkgsWithoutACK = queue.Queue(maxsize=self.windowSize)
        self.transferMethod = transferMethod
        self.bit = 1

    def create_timer(self, address):
        return RepeatingTimer(GBN_BASE_PACKAGE_TIMEOUT, sendWindow, self.transferMethod, self.sentPkgsWithoutACK, address)

    def send_file(self, file, address, timeout):
        
        self.timer = self.create_timer(address)
        self.timer.start()

        while self.nextSeqNumber <= self.windowSize:
            data = file.read(BUFSIZE)
            if not data:
                break
            self.transferMethod.sendMessage(self.nextSeqNumber, data, address)
            logging.info(f"Packet {self.nextSeqNumber} sent to {address}.")
            self.sentPkgsWithoutACK.put((self.nextSeqNumber, data))
            self.nextSeqNumber += 1
        

        while not self.sentPkgsWithoutACK.empty():
            try:
                message = self.transferMethod.recvMessage(0)
                logging.debug(f"base={self.base} seq_num={message.bit} type={message.type}")

                if message.type != ACK:
                    if message.type == FIN:
                        logging.info(f"{FIN} messsage received from {address}.")
                        self.transferMethod.sendMessage(self.nextSeqNumber, FIN_ACK.encode(), address)
                        logging.debug(f"{FIN_ACK} messsage sent to {address}.")
                    else:
                        logging.error(f"Unknown message received: {message.data[:15]}, from {address}")
                        self.transferMethod.sendMessage(self.nextSeqNumber, FIN.encode(), address)
                        logging.info(f"{FIN} messsage sent to {address}.")
                    logging.error("File transfer NOT completed")
                    return
                
                if self.base <= message.bit:
                    logging.debug(f"Restarting timer")
                    self.timer.end()
                    self.timer.cancel()
                    while self.base <= message.bit:
                        self.sentPkgsWithoutACK.get()
                        data = file.read(BUFSIZE)
                        if data:
                            self.transferMethod.sendMessage(self.nextSeqNumber, data, address)
                            logging.info(f"Packet {self.nextSeqNumber} sent to {address}.")
                            self.sentPkgsWithoutACK.put((self.nextSeqNumber, data))
                            self.nextSeqNumber += 1
                        self.base += 1
                    self.timer = self.create_timer(address)
                    self.timer.start()
                
            except Exception as e: # TODO: make it more specific
                pass
        
        self.transferMethod.sendMessage(self.nextSeqNumber, FIN.encode(), address)
        logging.info(f"{FIN} message sent to {address}.")
        logging.info("File transfer completed")
        self.timer.end()
        self.timer.cancel()


    def recv_file(self, file, address, lastSentMsg=None, lastRcvBit=None):
        lastSeqNum = 0

        message = self.transferMethod.recvMessage(timeout=GBN_RECEIVER_TIMEOUT)
        logging.debug(f"base={self.base} seq_num={message.bit} type={message.type}")

        while message.type == DATA:
            if message.bit == lastSeqNum + 1:
                file.write(message.data)
                lastSeqNum = message.bit

            self.transferMethod.sendMessage(lastSeqNum, ACK.encode(), address)

            message = self.transferMethod.recvMessage(timeout=GBN_RECEIVER_TIMEOUT)
            logging.debug(f"base={self.base} seq_num={message.bit} type={message.type}")
        
        if message.type == FIN:
            logging.info(f"{FIN} messsage received from {message.clientAddress}.")
            self.transferMethod.sendMessage(message.bit, FIN_ACK.encode(), message.clientAddress)
            logging.debug(f"{FIN_ACK} messsage sent to {message.clientAddress}.")
            logging.info(f"Received file from {message.clientAddress}")
        else:
            logging.error(f"Unknown message received {message.data[:15]} from {message.clientAddress}")
            self.transferMethod.sendMessage(message.bit, FIN.encode(), message.clientAddress)
            logging.debug(f"{FIN} messsage sent to {message.clientAddress}.")
            logging.info("File transfer NOT completed")

