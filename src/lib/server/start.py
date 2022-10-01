import os
import logging
from socket import socket, AF_INET, SOCK_DGRAM
import sys
from .argparser import parse_arguments
from .listener import listen


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
