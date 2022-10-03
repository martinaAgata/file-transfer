import logging
import queue
from .timer import RepeatingTimer
from .definitions import (BUFSIZE, GBN_BASE_PACKAGE_TIMEOUT, UPLOAD, DOWNLOAD, DATA,
                          FIN, FIN_ACK, ACK, NAK, TIMEOUT)

def sendWindow(transferMethod, queue, address):
    for (bit, data) in list(queue):
        transferMethod.sendMessage(bit, data, address)

class GoBackN:
    def __init__(self, transferMethod):
        self.nextSeqNumber = 1
        self.base = 1
        self.windowSize = 5
        self.timer = None
        self.sentPkgsWithoutACK = queue.Queue(maxsize=self.windowSize)
        self.transferMethod = transferMethod
        self.bit = 1

    def create_timer(self, address):
        return RepeatingTimer(4, sendWindow, self.transferMethod, self.sentPkgsWithoutACK, address)

    def send_file(self, file, address, timeout):
        
        self.timer = self.create_timer(address)
        self.timer.start()

        while self.nextSeqNumber <= self.windowSize:
            data = file.read(BUFSIZE)
            if not data:
                break
            self.transferMethod.sendMessage(self.nextSeqNumber, data, address)
            self.sentPkgsWithoutACK.put((self.nextSeqNumber, data))
            self.nextSeqNumber += 1
        

        while not self.sentPkgsWithoutACK.empty():
            try:
                message = self.transferMethod.recvMessage(0)

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
                    timer.cancel()
                    while self.base <= message.bit:
                        self.sentPkgsWithoutACK.get()
                        data = file.read(BUFSIZE)
                        if data:
                            self.transferMethod.sendMessage(self.nextSeqNumber, data, address)
                            self.sentPkgsWithoutACK.put((self.nextSeqNumber, data))
                            self.nextSeqNumber += 1
                        self.base += 1
                    timer = self.create_timer(address)
                    timer.start()
                
            except Exception as e:
                pass
                # logging.debug(f"No hay ACKS en el socket {e}")
        
        self.transferMethod.sendMessage(self.nextSeqNumber, FIN.encode(), address)
        logging.info(f"{FIN} messsage sent to {address}.")
        logging.info("File transfer completed")

        # while data or not self.sentPkgsWithoutACK.empty():
        #     logging.debug("Read data from file")

        #     # Si tengo espacio en la ventana para enviar datos, envio de a 1 paquete por iter
        #     if self.nextSeqNumber < (self.base + self.windowSize):
        #         self.transferMethod.sendMessage(self.nextSeqNumber, data, address)
        #         logging.debug("Sent data to server")
        #         # guardo el pkg enviado pero sin ACK
        #         self.sentPkgsWithoutACK.put((self.nextSeqNumber, data))
        #         # si es el primero en ser enviado de la ventana (base), inicio timer
        #         if self.base == nextseqnum:
        #             timer = RepeatingTimer(GBN_BASE_PACKAGE_TIMEOUT, sendWindow, self.transferMethod, queue, address)
        #             timer.start()
        #         # ya envie el pkg, envío el siguiente si está dentro de la ventana    
        #         nextseqnum += 1
        #         data = file.read(BUFSIZE)

        
        #     try:
        #         message = self.transferMethod.recvMessage(0)  # _ is serverAddress
        #         logging.debug(f"Received message {message} from server")

        #         if message.type != ACK:
        #             if message.type == FIN:
        #                 logging.info(f"{FIN} messsage received from {address}.")
        #                 self.transferMethod.sendMessage(self.nextSeqNumber, FIN_ACK.encode(), address)
        #                 logging.debug(f"{FIN_ACK} messsage sent to {address}.")
        #             else:
        #                 logging.error(f"Unknown message received: {message.data[:15]}, from {address}")
        #                 self.transferMethod.sendMessage(self.nextSeqNumber, FIN.encode(), address)
        #                 logging.info(f"{FIN} messsage sent to {address}.")
        #             logging.error("File transfer NOT completed")
        #             return
                
        #         # revisar nextSeqNum y actualizar en base a lo que llegó
        #         self.base = message.bit + 1
        #         for _ in range(self.base, message.bit):
        #             self.sentPkgsWithoutACK.get()

        #         if self.base == self.nextSeqNumber:
        #           timer.stop()
                    

        #     except Exception as e:
        #         logging.debug(f"Timeout from server {e}")
        


        #     logging.debug(f"{ACK} received from server")
            

        # # Inform the server that the download is finished
        # self.transferMethod.sendMessage(self.nextSeqNumber, FIN.encode(), address)
        # logging.debug(f"Sent {FIN} to server")

        # logging.info("File sent to server")

    def recv_file(self, file, address, lastSentMsg=None, lastRcvBit=None):
        lastSeqNum = 0

        message = self.transferMethod.recvMessage(timeout=15)

        while message.type == DATA:
            
            if message.bit == lastSeqNum + 1:
                file.write(message.data)
                lastSeqNum = message.bit

            self.transferMethod.sendMessage(lastSeqNum, ACK.encode(), address)
                
                
            message = self.transferMethod.recvMessage(timeout=15)
        
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

