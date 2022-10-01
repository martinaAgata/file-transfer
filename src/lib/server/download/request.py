import logging
import os
from lib.definitions import BUFSIZE, ACK, FIN, FIN_ACK, NAK


def handle(clientAddress, serverSocket, queue, dirpath, filename):
    logging.info("Handling download request")

    if not os.path.exists(dirpath + filename):
        logging.error(f"File does not exist: {dirpath}/{filename}")
        # Send filename does not exist NAK.
        serverSocket.sendto(f'{NAK} File does not exist.'.encode(), clientAddress)
        logging.debug(f"Sending {NAK} File does not exist to client {clientAddress}")
        return

    # Send filename received ACK.
    serverSocket.sendto(f'{ACK} Filename received.'.encode(), clientAddress)
    logging.debug(f"{ACK} Filename received sent to client {clientAddress}")

    file = open(dirpath + filename, 'rb')
    logging.debug(f"File to read from is {dirpath}/{filename}")

    send_file(file, serverSocket, clientAddress, queue)

    file.close()


def send_file(file, serverSocket, clientAddress, queue):
    # Read first BUFSIZE bytes of the file
    data = file.read(BUFSIZE)

    while data:
        logging.debug("Read data from file")
        # Send bytes to the client
        serverSocket.sendto(data, clientAddress)
        logging.debug(f"Sent data to client {clientAddress}")

        # Receive answer from the client
        message = queue.get()

        logging.debug(f"Received message {message.type} from client {clientAddress}")

        # Check that is ACK
        if message.type != ACK:
            logging.error(f"ACK not received from client {clientAddress}")
            break  # TODO: wouldn't it be a return instead of a break?

        # Read another BUFSIZE bytes
        data = file.read(BUFSIZE)

    if message.type == FIN:
        logging.info(f"Received file from client {message.clientAddress}")
        serverSocket.sendto(FIN_ACK.encode(), message.clientAddress)
    elif not data:
        # Inform the client that the download is finished
        serverSocket.sendto(FIN.encode(), clientAddress)
        logging.debug(f"Sent {FIN} to client {clientAddress}")
        logging.info(f"Sent file to client {clientAddress}")
    else:
        logging.info(
            f"ERROR: Received a {message.type} packet at the end" "of file upload"
        )
        # TODO: Check if sending FIN is the best choice to close the client.
        serverSocket.sendto(FIN.encode(), message.clientAddress)
