import logging
from socket import socket, AF_INET, SOCK_DGRAM
from .argparser import parse_arguments
from .request import handle


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

    handle(clientSocket, serverIP, port, filepath, filename)

    clientSocket.close()
    logging.debug(f"Socket {clientSocket} closed")
