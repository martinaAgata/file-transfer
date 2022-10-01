import logging
from .client_handler import ClientHandler
from .message import Message
from lib.definitions import BUFSIZE, UPLOAD, DOWNLOAD, NAK, FIN, FIN_ACK


def listen(serverSocket, dirpath):
    logging.info("Socket created and listening for requests")

    clientHandler = None
    clientsDict = {}

    while True:
        try:
            # Receive filepath first.
            firstMessage, clientAddress = serverSocket.recvfrom(BUFSIZE)

            message = Message(firstMessage, clientAddress)

            # Get the clientHanlder
            if clientAddress in clientsDict:
                # OLD CLIENT
                clientHandler = clientsDict[clientAddress]
            else:
                # NEW CLIENT
                # TODO: maybe check if file exists or NAK
                if message.type in [UPLOAD, DOWNLOAD]:
                    clientHandler = ClientHandler(clientAddress, serverSocket, dirpath)
                    clientHandler.start_thread()
                    clientsDict[clientAddress] = clientHandler
                else:
                    # TODO: log me
                    # TODO: send reasons for NAK
                    serverSocket.sendto(NAK.encode(), clientAddress)
                    continue

            # Send the message to the clientHandler
            clientHandler.send(message)

            # TODO: Check that every time that a FIN is send, the thread go to
            # the end of the scope.
            #
            # If FIN -> Join client, and send FIN_ACK
            # If FIN_ACK -> We've already sent FIN, so just join client
            # In both cases, we must remove clientHandler from clientsDict
            if message.type in [FIN, FIN_ACK]:
                clientHandler.join()
                logging.debug(f"Client {clientAddress} thread was joined")
                del clientsDict[clientAddress]
                logging.debug(f"Client {clientAddress} has been disconnected")
        except KeyboardInterrupt:
            logging.debug("A keyboard interrupt signal has been received")
            print()
            break

    # This code is unreachable until we set ctrl+c signal
    for (clientAddress, clientHandler) in clientsDict:
        message = Message("FIN".encode(), clientAddress)
        clientHandler.send(message)
        clientHandler.join()
        logging.debug(f"Client {clientAddress} thread was joined")

    clientsDict.clear()
