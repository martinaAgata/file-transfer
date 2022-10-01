import logging
import os
from lib.client import decode, encode
from lib.definitions import BUFSIZE, ACK, DATA, FIN, UPLOAD
from lib.client.communication import send_filename


def handle(clientSocket):
    logging.info("Handling upload")

    if not os.path.exists(filepath + filename):
        logging.error(
            f"Requested source file {filepath}/{filename} does not exists")
        return

    try:
        send_filename(UPLOAD, filename, (serverIP, port), clientSocket)
    except NameError as err:
        logging.error(
            f"Message received from server is not an ACK: {format(err)}")
        return

    # Open file for sending using byte-array option.
    file = open(filepath + filename, "rb")

    try:
        send_file(file, clientSocket)
    except BaseException as err:
        logging.error(
            f"An error occurred when sending file to server: {format(err)}")
    finally:
        # Close everything
        file.close()


def send_file(file, clientSocket):
    data = file.read(BUFSIZE)

    while data:
        logging.debug("Read data from file")

        clientSocket.sendto(encode(DATA, data), (serverIP, port))
        logging.debug("Sent data to server")
        message, _ = clientSocket.recvfrom(BUFSIZE)  # second element is serverAddress
        logging.debug(f"Received message {message} from server")
        (type, response) = decode(message)

        if type != ACK:
            # TODO: Think a better error
            raise BaseException(response)

        logging.debug("ACK received from server")
        data = file.read(BUFSIZE)

    # Inform the server that the download is finished
    clientSocket.sendto(encode(FIN), (serverIP, port))
    logging.debug("Sent FIN to server")

    logging.info("File sent to server")
