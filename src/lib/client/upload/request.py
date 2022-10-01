import logging
import os
from lib.definitions import BUFSIZE, ACK, FIN, UPLOAD
from lib.client.communication import send_filename
from lib.utils import is_ack


def handle(clientSocket, serverIP, port, filepath, filename):
    logging.info(f"Handling {UPLOAD}")

    if not os.path.exists(filepath + filename):
        logging.error(
            f"Requested source file {filepath}/{filename} does not exists")
        return

    try:
        send_filename(clientSocket, UPLOAD, serverIP, port, filename)
    except NameError as err:
        logging.error(
            f"Message received from server is not an {ACK}: {format(err)}")
        return

    # Open file for sending using byte-array option.
    file = open(filepath + filename, "rb")

    try:
        send_file(file, clientSocket, serverIP, port)
    except BaseException as err:
        logging.error(
            f"An error occurred when sending file to server: {format(err)}")
    finally:
        # Close everything
        file.close()


def send_file(file, clientSocket, serverIP, port):
    data = file.read(BUFSIZE)

    while data:
        logging.debug("Read data from file")

        clientSocket.sendto(data, (serverIP, port))
        logging.debug("Sent data to server")
        message, _ = clientSocket.recvfrom(BUFSIZE)  # _ is serverAddress
        logging.debug(f"Received message {message} from server")
        (ack, response) = is_ack(message)

        if not ack:
            # TODO: Think a better error
            raise BaseException(response)

        logging.debug(f"{ACK} received from server")
        data = file.read(BUFSIZE)

    # Inform the server that the download is finished
    clientSocket.sendto(FIN.encode(), (serverIP, port))
    logging.debug(f"Sent {FIN} to server")

    logging.info("File sent to server")
