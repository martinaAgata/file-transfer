import os
import logging
from socket import socket, AF_INET, SOCK_DGRAM
from lib.definitions import *
from .argparser import parse_arguments


def process_first_message(encodedFirstMessage):

    firstMessage = encodedFirstMessage.decode().split()

    return (firstMessage[0], firstMessage[1])


def recv_file(file, serverSocket):
    # Receive file content.
    maybeFileContent, clientAddress = serverSocket.recvfrom(BUFSIZE)

    # TODO: Think about a better way to end the transfer
    while maybeFileContent != "END".encode():
        logging.debug(
            f"Received file content from client {clientAddress}")

        # Write file content to new file
        file.write(maybeFileContent)
        logging.debug("File content written")

        # Send file content received ACK.
        serverSocket.sendto('ACK'.encode(), clientAddress)
        logging.debug(f"ACK sent to client {clientAddress}")

        maybeFileContent, clientAddress = serverSocket.recvfrom(BUFSIZE)

    logging.info(f"Received file from client {clientAddress}")


def send_file(file, serverSocket, clientAddress):
    data = file.read(BUFSIZE)

    while data:
        logging.debug("Read data from file")
        serverSocket.sendto(data, clientAddress)
        logging.debug(f"Sent data to client {clientAddress}")

        message, serverAddress = serverSocket.recvfrom(BUFSIZE)
        logging.debug(
            f"Received message {message} from client {clientAddress}")

        if message.decode() != 'ACK':
            logging.error(f"ACK not received from client {clientAddress}")
            break  # TODO: wouldn't it be a return instead of a break?

        data = file.read(BUFSIZE)

    # inform the client that the download is finished
    serverSocket.sendto("FIN".encode(), clientAddress)
    logging.debug(f"Sent FIN to client {clientAddress}")

    logging.info(f"Sent file to client {clientAddress}")


def handle_upload_request(serverSocket, clientAddress, filename):
    logging.info("Handling upload request")

    # Send filename received ACK.
    serverSocket.sendto('ACK Filename received.'.encode(), clientAddress)
    logging.debug(f"ACK filename received sent to client {clientAddress}")

    # Create new file where to put the content of the file to receive.
    # Opens a file for writing. Creates a new file if it does not exist
    # or truncates the file if it exists.
    file = open(dirpath + filename, 'wb')
    logging.debug(f"File to write in is {dirpath}/{filename}")

    recv_file(file, serverSocket)

    file.close()


def handle_download_request(serverSocket, clientAddress, filename):
    logging.info("Handling download request")

    if not os.path.exists(dirpath + filename):
        logging.error(f"File does not exist: {dirpath}/{filename}")
        # Send filename does not exist NAK.
        serverSocket.sendto('NAK File does not exist.'.encode(), clientAddress)
        logging.debug(
            f"Sending NAK File does not exist to client {clientAddress}")
        return

    # Send filename received ACK.
    serverSocket.sendto('ACK Filename received.'.encode(), clientAddress)
    logging.debug(
        f"ACK Filename received sent to client {clientAddress}")

    file = open(dirpath + filename, 'rb')
    logging.debug(f"File to read from is {dirpath}/{filename}")

    send_file(file, serverSocket, clientAddress)

    file.close()


def listen(serverSocket, dirpath):
    logging.info("Socket created and listening for requests")

    while True:
        # Receive filepath first.
        firstMessage, clientAddress = serverSocket.recvfrom(BUFSIZE)

        logging.debug(f"First message received from {clientAddress}")
        logging.debug(f"First message content: {firstMessage}")
        (command, filename) = process_first_message(firstMessage)
        logging.info(f"Received {command} command for file {filename}")

        # TODO: Handle case where command is not upload and download
        if command == UPLOAD:
            handle_upload_request(serverSocket, clientAddress, filename)
        elif command == DOWNLOAD:
            handle_download_request(serverSocket, clientAddress, filename)
        else:
            logging.error(
                f"Received an invalid command from client {clientAddress}")



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
    logging.info("Socket closed")

