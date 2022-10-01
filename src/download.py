import argparse
import logging
import os
from socket import socket, AF_INET, SOCK_DGRAM
from lib.definitions import (BUFSIZE, FIN, ACK, DOWNLOAD,
                             DEFAULT_LOGGING_LEVEL,
                             DEFAULT_SERVER_IP,
                             DEFAULT_SERVER_PORT,
                             DEFAULT_DOWNLOAD_FILEPATH)
from lib.utils import send_filename


def recv_file(file, clientSocket):
    # Receive file content.
    maybeFileContent, serverAddress = clientSocket.recvfrom(BUFSIZE)

    while maybeFileContent != FIN.encode():
        logging.debug("Received file content from server")

        # Write file content to new file
        file.write(maybeFileContent)
        logging.debug("File content written to file")

        # Send file content received ACK.
        clientSocket.sendto(ACK.encode(), serverAddress)
        logging.debug(f"Sent {ACK} to server")
        maybeFileContent, serverAddress = clientSocket.recvfrom(BUFSIZE)

    print("Received file content from the Server.")
    logging.debug(f"Received {FIN} message from server")

    logging.info("File downloaded from server")


def handle_download_request(clientSocket, serverIP, port, filepath, filename):
    logging.info("Handling download")

    if not os.path.exists(filepath):
        logging.error(
            f"Requested destination file {filepath} does not exists")
        return

    try:
        send_filename(clientSocket, DOWNLOAD, serverIP, port, filename)
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
        logging.debug("File was closed")


def parse_arguments():
    argParser = argparse.ArgumentParser(
        prog=DOWNLOAD, description='Download a file from a given server')

    group = argParser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose',
                       help='increase output verbosity',
                       action="store_const",
                       dest="loglevel", const=logging.DEBUG,
                       default=DEFAULT_LOGGING_LEVEL)
    group.add_argument('-q', '--quiet',
                       help='decrease output verbosity', action="store_const",
                       dest="loglevel", const=logging.CRITICAL,
                       default=DEFAULT_LOGGING_LEVEL)

    argParser.add_argument('-H', '--host',
                           type=str,
                           help='server IP address',
                           default=DEFAULT_SERVER_IP,
                           metavar='ADDR')
    argParser.add_argument('-p', '--port',
                           type=int,
                           help='server port',
                           default=DEFAULT_SERVER_PORT)
    argParser.add_argument('-d', '--dst',
                           type=str,
                           help='destination file path',
                           default=DEFAULT_DOWNLOAD_FILEPATH,
                           metavar='FILEPATH')
    argParser.add_argument('-n', '--name',
                           type=str,
                           help='file name',
                           required=True,
                           metavar='FILENAME')

    return argParser.parse_args()


def start_client():
    args = parse_arguments()

    logging.basicConfig(level=args.loglevel)
    logging.info("Initializing upload client")
    logging.debug("Arguments parsed")

    serverIP = args.host
    port = args.port
    filepath = args.dst
    filename = args.name

    logging.debug(f"Server IP address: {serverIP}")
    logging.debug(f"Server port: {port}")
    logging.debug(f"Filepath: {filepath}")
    logging.debug(f"Filename: {filename}")

    clientSocket = socket(AF_INET, SOCK_DGRAM)

    handle_download_request(clientSocket, serverIP, port, filepath, filename)

    clientSocket.close()
    logging.debug(f"Socket {clientSocket} closed")


def main():
    start_client()


if __name__ == "__main__":
    main()