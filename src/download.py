import argparse
import logging
import os
from socket import socket, AF_INET, SOCK_DGRAM
from lib.definitions import (DEFAULT_DOWNLOAD_PROTOCOL_BIT, FIN, ACK,
                             DOWNLOAD, GBN_BIT, SNW_BIT,
                             TIMEOUT, FIN_ACK, ACK_ACK,
                             DEFAULT_LOGGING_LEVEL,
                             DEFAULT_SERVER_IP,
                             DEFAULT_SERVER_PORT,
                             DEFAULT_DOWNLOAD_FILEPATH)
from lib.only_socket_transfer_method import OnlySocketTransferMethod
from lib.utils import (get_transfer_protocol,
                       protocol_bit_format,
                       recv_or_retry_send)


def handle_download_request(protocol_bit, clientSocket,
                            serverAddress, filepath, filename):
    logging.info("Handling downloads")

    if not os.path.exists(filepath):
        logging.info("Created destination dir because it did not exist")
        os.mkdir(filepath)

    if not os.path.isdir(filepath):
        logging.error(f"Requested destination dir {filepath} is not a dir")
        return

    transferMethod = OnlySocketTransferMethod(clientSocket)

    # Send the UPLOAD filename to the client
    downloadCmd = (DOWNLOAD + ' ' + filename).encode()

    transferMethod.sendMessage(protocol_bit, downloadCmd, serverAddress)
    logging.debug(f"[HANDSHAKE] Sending {DOWNLOAD} request for file {filename}"
                  + f" with {protocol_bit_format(protocol_bit)}")

    # Recv ACK
    try:
        # message = transferMethod.recvMessage(TIMEOUT)
        message = recv_or_retry_send(transferMethod, downloadCmd, serverAddress,
                                     protocol_bit, TIMEOUT)
    except Exception:
        logging.error("Timeout while waiting for filename ACK")
        return
    logging.info(f"{message.type} was received")

    if message.type != ACK:
        if message.type == FIN:
            logging.info(f"{FIN} messsage received from {serverAddress}")
            transferMethod.sendMessage(1, FIN_ACK.encode(), serverAddress)
            logging.debug(f"{FIN_ACK} messsage sent to {serverAddress}")
        else:
            logging.error(
                f"Unknown message received: {message.type}, from {serverAddress}")
            transferMethod.sendMessage(1, FIN.encode(), serverAddress)
            logging.info(f"{FIN} message sent to {serverAddress}")
        logging.error("File transfer NOT started")
        return

    logging.debug(f"[HANDSHAKE] Received {DOWNLOAD} request ACK for file {filename}")

    # Open file for receiving using byte-array option.
    # If file does not exist, then creates a new one.
    file = open(filepath + filename, "wb")
    logging.debug(f"File to write in is {filepath}{filename}")

    transferProtocol = get_transfer_protocol(protocol_bit, transferMethod)
    transferProtocol.recv_file(file, serverAddress)

    file.close()


def parse_arguments():
    argParser = argparse.ArgumentParser(
        prog='download', description='Download a file from a given server')

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
    
    gbn_def = snw_def = ""
    if DEFAULT_DOWNLOAD_PROTOCOL_BIT == GBN_BIT:
        gbn_def = "(default)"
    else:
        snw_def = "(default)"

    protocols = argParser.add_mutually_exclusive_group()
    protocols.add_argument('--gbn',
                           help=f'use Go-Back-N protocol {gbn_def}',
                           action="store_const",
                           dest="protocol", const=GBN_BIT,
                           default=DEFAULT_DOWNLOAD_PROTOCOL_BIT)
    protocols.add_argument('--snw',
                           help=f'use Stop & Wait protocol {snw_def}', action="store_const",
                           dest="protocol", const=SNW_BIT,
                           default=DEFAULT_DOWNLOAD_PROTOCOL_BIT)

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
    protocol = args.protocol

    if filepath[-1] != '/':
        filepath += '/'

    logging.debug(f"Server IP address: {serverIP}")
    logging.debug(f"Server port: {port}")
    logging.debug(f"Filepath: {filepath}")
    logging.debug(f"Filename: {filename}")
    logging.debug(f"Protocol: {protocol_bit_format(protocol)}")

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    serverAddress = (serverIP, port)

    handle_download_request(protocol, clientSocket, serverAddress, filepath, filename)

    clientSocket.close()
    logging.debug(f"Socket {clientSocket} closed")


def main():
    start_client()


if __name__ == "__main__":
    main()
