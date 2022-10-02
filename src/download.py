import argparse
import logging
import os
from socket import socket, AF_INET, SOCK_DGRAM
from lib.definitions import (BUFSIZE, FIN, ACK, DOWNLOAD,
                             TIMEOUT, FIN_ACK,
                             DEFAULT_LOGGING_LEVEL,
                             DEFAULT_SERVER_IP,
                             DEFAULT_SERVER_PORT,
                             DEFAULT_DOWNLOAD_FILEPATH)
from lib.utils import send_filename
from lib.StopAndWait import StopAndWait
from lib.UDPHandler import send
from lib.only_socket_transfer_method import OnlySocketTransferMethod

def handle_download_request(clientSocket, serverAddress):
    logging.info("Handling downloads")

    if not os.path.exists(filepath):
        logging.error(
            f"Requested source file {filepath} does not exists")
        return

    transferMethod = OnlySocketTransferMethod(clientSocket)
    stopAndWait = StopAndWait(transferMethod)

    # Send the UPLOAD filename to the client
    downloadCmd = (DOWNLOAD + ' ' + filename).encode()
    transferMethod.sendMessage(1, downloadCmd, serverAddress)

    # Recv ACK
    try:
        message = transferMethod.recvMessage(TIMEOUT)
    except Exception:
        logging.error(
            f"Timeout while waiting for filename ACK.")
        return

    if message.type != ACK:
        if message.type == FIN:
            logging.info(f"{FIN} messsage received from {serverAddress}.")
            transferMethod.sendMessage(1, FIN_ACK.encode(), serverAddress)
            logging.debug(f"{FIN_ACK} messsage sent to {serverAddress}.")
        else:
            logging.error(f"Unknown message received: {message.type}, from {serverAddress}")
            transferMethod.sendMessage(1, FIN.encode(), serverAddress)
            logging.info(f"{FIN} messsage sent to {serverAddress}.")
        logging.error("File transfer NOT started")
        return

    # Open file for receiving using byte-array option.
    # If file does not exist, then creates a new one.
    file = open(filepath + filename, "wb")
    logging.debug(f"File to write in is {filepath}/{filename}")

    stopAndWait.recv_file(file, serverAddress)

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

    if filepath[-1] != '/':
        filepath +=  '/'

    logging.debug(f"Server IP address: {serverIP}")
    logging.debug(f"Server port: {port}")
    logging.debug(f"Filepath: {filepath}")
    logging.debug(f"Filename: {filename}")

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    serverAddress = (serverIP, port)

    handle_download_request(clientSocket, serverAddress)

    clientSocket.close()
    logging.debug(f"Socket {clientSocket} closed")


def main():
    start_client()


if __name__ == "__main__":
    main()