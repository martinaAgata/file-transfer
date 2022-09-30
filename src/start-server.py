import argparse
import logging
import os
import sys
from socket import socket, AF_INET, SOCK_DGRAM
from lib.client_handler import ClientHandler
from lib.message import Message
from lib.definitions import (BUFSIZE, UPLOAD, DOWNLOAD, NAK, FIN, FIN_ACK,
                             DEFAULT_LOGGING_LEVEL, DEFAULT_SERVER_IP,
                             DEFAULT_SERVER_PORT, DEFAULT_DIRPATH)


def listen(serverSocket, dirpath):
    logging.info("Socket created and listening for requests")

    clientHandler = None
    clientsDict = {}

    while True:
        try:
            # Receive filepath first.
            firstMessage, clientAddress = serverSocket.recvfrom(BUFSIZE)

            message = Message(firstMessage, clientAddress)

            # Get the clientHanlder
            if clientAddress in clientsDict:
                # OLD CLIENT
                clientHandler = clientsDict[clientAddress]
            else:
                # NEW CLIENT
                # TODO: maybe check if file exists or NAK
                if message.type in [UPLOAD, DOWNLOAD]:
                    clientHandler = ClientHandler(
                        clientAddress,
                        serverSocket,
                        dirpath)
                    clientHandler.start_thread()
                    clientsDict[clientAddress] = clientHandler
                else:
                    # TODO: log me
                    # TODO: send reasons for NAK
                    serverSocket.sendto(NAK.encode(), clientAddress)
                    continue

            # Send the message to the clientHandler
            clientHandler.send(message)

            # TODO: Check that every time that a FIN is send, the thread go to
            # the end of the scope.
            #
            # If FIN -> Join client, and send FIN_ACK
            # If FIN_ACK -> We've already sent FIN, so just join client
            # In both cases, we must remove clientHandler from clientsDict
            if message.type in [FIN, FIN_ACK]:
                clientHandler.join()
                logging.debug(f"Client {clientAddress} thread was joined")
                del clientsDict[clientAddress]
                logging.debug(f"Client {clientAddress} has been disconnected")
        except KeyboardInterrupt:
            logging.debug("A keyboard interrupt signal has been received")
            print()
            break

    # This code is unreachable until we set ctrl+c signal
    for (clientAddress, clientHandler) in clientsDict:
        message = Message("FIN".encode(), clientAddress)
        clientHandler.send(message)
        clientHandler.join()
        logging.debug(f"Client {clientAddress} thread was joined")

    clientsDict.clear()


def parse_arguments():
    argParser = argparse.ArgumentParser(
        prog='start-server',
        description='Start the server with a specific configuration')

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
                           help='service IP address',
                           default=DEFAULT_SERVER_IP,
                           metavar='ADDR')
    argParser.add_argument('-p', '--port',
                           type=int,
                           help='service port',
                           default=DEFAULT_SERVER_PORT)
    argParser.add_argument('-s', '--storage',
                           type=str,
                           help='storagte dir path',
                           default=DEFAULT_DIRPATH,
                           metavar='DIRPATH')

    return argParser.parse_args()


def start_server():
    args = parse_arguments()

    logging.basicConfig(level=args.loglevel)
    logging.info("Initializing server")
    logging.debug("Arguments parsed")

    host = args.host
    port = args.port
    dirpath = args.storage

    logging.debug(f"Host IP address: {host}")
    logging.debug(f"Host port: {port}")
    logging.debug(f"Directory path: {dirpath}")

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((host, port))

    # Create /files directory if not exist
    if not os.path.isdir(dirpath):
        logging.debug("Directory created because it did not exist")
        os.mkdir(dirpath)

    listen(serverSocket, dirpath)

    serverSocket.close()
    logging.info("Server exiting")
    sys.exit()


def main():
    start_server()


if __name__ == "__main__":
    main()
