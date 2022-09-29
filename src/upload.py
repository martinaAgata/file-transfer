import argparse
import logging
import os
from socket import socket, AF_INET, SOCK_DGRAM
from lib.definitions import (BUFSIZE, ACK, FIN, UPLOAD,
                             DEFAULT_LOGGING_LEVEL,
                             DEFAULT_SERVER_IP,
                             DEFAULT_SERVER_PORT,
                             DEFAULT_UPLOAD_FILEPATH)
from lib.utils import send_filename, is_ack


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


def handle_upload_request(clientSocket, serverIP, port, filepath, filename):
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


def parse_arguments():
    argParser = argparse.ArgumentParser(
        prog=UPLOAD, description='Upload a file to a given server')

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
    argParser.add_argument('-s', '--src',
                           type=str,
                           help='source file path',
                           default=DEFAULT_UPLOAD_FILEPATH,
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
    filepath = args.src
    filename = args.name

    logging.debug(f"Server IP address: {serverIP}")
    logging.debug(f"Server port: {port}")
    logging.debug(f"Filepath: {filepath}")
    logging.debug(f"Filename: {filename}")

    clientSocket = socket(AF_INET, SOCK_DGRAM)

    handle_upload_request(clientSocket, serverIP, port, filepath, filename)

    clientSocket.close()
    logging.debug(f"Socket {clientSocket} closed")



def main():
    start_client()


if __name__ == "__main__":
    main()
