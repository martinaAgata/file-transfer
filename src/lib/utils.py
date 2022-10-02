import logging
import os
from .definitions import (BUFSIZE, UPLOAD, DOWNLOAD, DATA,
                          FIN, FIN_ACK, ACK, NAK, TIMEOUT)
from .StopAndWait import StopAndWait
from .UDPHandler import send


def handle_upload_request(clientAddress,
                          transfer_protocol,
                          dirpath,
                          filename,
                          lastBit):
    logging.info("Handling upload request")

    # Send filename received ACK.
    transfer_protocol.transferMethod.sendMessage(1, ACK.encode(), clientAddress)
    logging.debug(f"{ACK} filename received sent to client {clientAddress}")

    # Create new file where to put the content of the file to receive.
    # Opens a file for writing. Creates a new file if it does not exist
    # or truncates the file if it exists.
    file = open(dirpath + filename, 'wb')
    logging.debug(f"File to write in is at {dirpath}{filename}")

    transfer_protocol.recv_file(file, clientAddress, lastSentMsg=ACK.encode(), lastRcvBit=transfer_protocol.bit)

    file.close()


def handle_download_request(clientAddress,
                            transfer_protocol,
                            dirpath,
                            filename,
                            lastBit):
    logging.info("Handling download request")

    if not os.path.exists(dirpath + filename):
        logging.error(f"File does not exist: {dirpath}/{filename}")
        # Send filename does not exist NAK.
        transfer_protocol.transferMethod.sendMessage(1, FIN.encode(), clientAddress)
        logging.debug(
            f"Sending {FIN} File does not exist to client {clientAddress}")
        return

    # Send filename received ACK.
    transfer_protocol.transferMethod.sendMessage(1, ACK.encode(), clientAddress)

    logging.debug(
        f"{ACK} Filename received sent to client {clientAddress}")

    file = open(dirpath + filename, 'rb')
    logging.debug(f"File to read from is {dirpath}/{filename}")

    transfer_protocol.send_file(file, clientAddress, TIMEOUT)

    file.close()


def handle_action(address, transfer_protocol, dirpath):
    try:
        action = transfer_protocol.transferMethod.recvMessage(TIMEOUT)
        if action.type == UPLOAD:
            handle_upload_request(address, transfer_protocol, dirpath, action.data, transfer_protocol.bit)
        elif action.type == DOWNLOAD:
            handle_download_request(address, transfer_protocol, dirpath, action.data, transfer_protocol.bit)
        else:
            logging.error(
                f"Received an invalid command from client {address}")
    except Exception as err:
        logging.error(f"An error occurred when receiving command: {format(err)}")
        transfer_protocol.transferMethod.sendMessage(1, FIN.encode(), address)

