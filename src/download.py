import argparse
from socket import socket, AF_INET, SOCK_DGRAM
import os
from StopAndWait import *

DEFAULT_SERVER_IP = '127.0.0.1'
DEFAULT_SERVER_PORT = 12000
BUFSIZE = 2048
DEFAULT_DOWNLOAD_FILEPATH = 'lib/resources/'
DEFAULT_LOGGING_LEVEL = logging.INFO

# Splits message into [ACK | NAK] + data

def handle_download_request(clientSocket):
    logging.info("Handling download")

    if not os.path.exists(filepath):
        logging.error(
            f"Requested destination file {filepath} does not exists")
        return

    stopAndWait = StopAndWait(clientSocket)
    # Setting timeout only for first message
    clientSocket.settimeout(4)
    try:
        stopAndWait.send_filename('download', filename, serverIP, port)
    except NameError as err:
        logging.error(
            f"Message received from server is not an ACK: {format(err)}")
        return
    # Now the client is the one who receives the data, so
    # it shouldn't have a timeout
    clientSocket.settimeout(None)

    # Open file for receiving using byte-array option.
    # If file does not exist, then creates a new one.
    file = open(filepath + filename, "wb")

    try:
        bit, maybeFileContent, serverAddress = recv(clientSocket)
        stopAndWait.recv_file(maybeFileContent, file, serverAddress, bit)
        logging.info(f"Received file from server {serverAddress}")
    except BaseException as err:
        logging.error(
            f"An error occurred when receiving file from server: {format(err)}")
    finally:
        # Close everything
        file.close()


def parse_arguments():
    argParser = argparse.ArgumentParser(
        prog='upload', description='Download a file from a given server')

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

    global serverIP
    serverIP = args.host
    global port
    port = args.port
    global filepath
    filepath = args.dst
    global filename
    filename = args.name

    logging.debug(f"Server IP address: {serverIP}")
    logging.debug(f"Server port: {port}")
    logging.debug(f"Filepath: {filepath}")
    logging.debug(f"Filename: {filename}")

    clientSocket = socket(AF_INET, SOCK_DGRAM)

    handle_download_request(clientSocket)

    clientSocket.close()
    logging.debug(f"Socket {clientSocket} closed")


def main():
    start_client()


if __name__ == "__main__":
    main()
