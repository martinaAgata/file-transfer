import logging
import queue
from .timer import TimerPackageResender
from .definitions import (BUFSIZE, UPLOAD, DOWNLOAD, DATA,
                          FIN, FIN_ACK, ACK, NAK, TIMEOUT)

class GoBackN:
    def __init__(self, transferMethod):
        self.nextSeqNumber = 0
        self.base = 0
        self.windowSize = 0
        self.timer = None
        self.sentPkgsWithoutACK = queue.Queue(max_size=self.windowSize)
        self.transferMethod = transferMethod

    def send_file(self, file, address, timeout):
        data = file.read(BUFSIZE)

        while data:
            logging.debug("Read data from file")

            # Si tengo espacio en la ventana para enviar datos, envio de a 1 paquete por iter
            if self.nextSeqNumber < (self.base + self.windowSize):
                self.transferMethod.sendMessage(self.nextSeqNumber, data, address)
                logging.debug("Sent data to server")
                # guardo el pkg enviado pero sin ACK
                self.sentPkgsWithoutACK.put((self.nextSeqNumber, data))
                # si es el primero en ser enviado de la ventana (base), inicio timer
                if self.base == nextseqnum:
                    timer = TimerPackageResender(self.transferMethod, self.sentPkgsWithoutACK, address)
                    timer.start()
                # ya envie el pkg, envío el siguiente si está dentro de la ventana    
                nextseqnum += 1

        
            try:
                message = self.transferMethod.recvMessage(0)  # _ is serverAddress
                logging.debug(f"Received message {message} from server")

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
                
                # revisar nextSeqNum y actualizar en base a lo que llegó
                # sentPkgsWithoutACK.get()
                # if base == nextseqnum:
                #   timer.stop()
                    

            except BaseException as e:
                raise e
            except Exception as e:
                logging.debug(f"Timeout from server {e}")
        


            logging.debug(f"{ACK} received from server")
            data = file.read(BUFSIZE)

        # Inform the server that the download is finished
        self.transferMethod.sendMessage(self.nextSeqNumber, FIN.encode(), address)
        logging.debug(f"Sent {FIN} to server")

        logging.info("File sent to server")

    def recv_file(self, file, address, lastSentMsg=None, lastRcvBit=None):
        return

