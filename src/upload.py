import argparse
import logging
import os
from socket import socket, AF_INET, SOCK_DGRAM
from lib.definitions import (BUFSIZE, ACK, FIN, UPLOAD, FIN_ACK,
                             DEFAULT_LOGGING_LEVEL,
                             DEFAULT_SERVER_IP,
                             DEFAULT_SERVER_PORT,
                             DEFAULT_UPLOAD_FILEPATH,
                             TIMEOUT)
from lib.StopAndWait import StopAndWait
from lib.UDPHandler import send
from lib.only_socket_transfer_method import OnlySocketTransferMethod
from lib.GoBackN import GoBackN


def handle_upload_request(clientSocket, serverAddress):
    logging.info("Handling upload")

    # Check that file exists
    if not os.path.exists(filepath + filename):
        logging.error(
            f"Requested source file {filepath}/{filename} does not exists")
        return

    transferMethod = OnlySocketTransferMethod(clientSocket)

    # Send the UPLOAD filename to the client
    uploadCmd = (UPLOAD + ' ' + filename).encode()

    # We use stop and wait only in the beginning, just in cause that the ACK from the server get lost.
    stopAndWait = StopAndWait(transferMethod)
    transferMethod.sendMessage(stopAndWait.bit, uploadCmd, serverAddress)

    # Recv ACK
    try:
        message = stopAndWait.receive(serverAddress,
                                      lastSentMsg=uploadCmd,
                                      lastSentBit=stopAndWait.bit,
                                      timeout=TIMEOUT)
    except Exception:
        logging.error("Timeout while waiting for filename ACK.")
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

    # Open file for sending using byte-array option.
    file = open(filepath + filename, "rb")
    logging.debug(f"File to read from is {filepath}/{filename}")
    
    # transferProtocol = StopAndWait(transferMethod)
    transferProtocol = GoBackN(transferMethod)
    transferProtocol.send_file(file, serverAddress, TIMEOUT)

    file.close()


def parse_arguments():
    argParser = argparse.ArgumentParser(
        prog='upload', description='Upload a file to a given server')

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

    global serverIP
    serverIP = args.host
    global port
    port = args.port
    global filepath
    filepath = args.src
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

    handle_upload_request(clientSocket, serverAddress)

    clientSocket.close()
    logging.debug(f"Socket {clientSocket} closed")


def main():
    start_client()


if __name__ == "__main__":
    main()