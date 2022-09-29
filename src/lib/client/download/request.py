import logging
import os
from lib.client.communication import send_filename
from lib.definitions import *
from lib.client import encode, decode

def handle(clientSocket):
    logging.info("Handling download")

    if not os.path.exists(filepath):
        logging.error(
            f"Requested destination file {filepath} does not exists")
        return

    try:
        send_filename(DOWNLOAD, filename, (serverIP, port), clientSocket)
    except NameError as err:
        logging.error(
            f"Message received from server is not an ACK: {format(err)}")
        return

    # Open file for sending using byte-array option.
    # If file does not exist, then creates a new one.
    file = open(filepath + filename, "wb")

    try:
        recv_file(file, clientSocket)
    except BaseException as err:
        logging.error(
            f"An error occurred when sending file to server: {format(err)}")
    finally:
        # Close everything
        file.close()

def recv_file(file, clientSocket):
    # Receive file content.
    maybeFileContent, serverAddress = clientSocket.recvfrom(BUFSIZE)

    while maybeFileContent != encode(FIN):
        logging.debug("Received file content from server")

        # Write file content to new file
        type, fileContent = decode(maybeFileContent)
        if type == DATA:
            file.write(fileContent)
            logging.debug("File content written to file")
            # Send file content received ACK.
            clientSocket.sendto(encode(ACK), serverAddress)
            logging.debug("Sent ACK to server")

        maybeFileContent, serverAddress = clientSocket.recvfrom(BUFSIZE)

    print('Received file content from the Server.')
    logging.debug("Received FIN message from server")

    logging.info("File downloaded from server")
