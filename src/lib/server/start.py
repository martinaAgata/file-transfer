import os
import logging
from socket import socket, AF_INET, SOCK_DGRAM
from lib.definitions import *
from .argparser import parse_arguments
from lib.client_handler import ClientHandler
from lib.message import Message


def process_first_message(encodedFirstMessage):

    firstMessage = encodedFirstMessage.decode().split()

    return (firstMessage[0], firstMessage[1])


def recv_file(file, serverSocket, queue):
    # Receive file content (should be first packet).
    message = queue.get()

    # TODO: Think about a better way to end the transfer.
    # TODO: Perhaps it could stop iterating if type IS NOT DATA.
    while message.type == DATA:
        logging.debug(
            f"Received file content from client {message.clientAddress}")

        # Write file content to new file
        file.write(message.data)
        logging.debug("File content written")

        # Send file content received ACK.
        serverSocket.sendto('ACK'.encode(), message.clientAddress)
        logging.debug(f"ACK sent to client {message.clientAddress}")

        message = queue.get()

    if message.type == FIN:
        logging.info(f"Received file from client {message.clientAddress}")
        serverSocket.sendto('FIN_ACK'.encode(), message.clientAddress)
    else:
        logging.info(f"ERROR: Received a {message.type} packet at the end of file upload")
        # TODO: Check if sending FIN is the best choice.
        serverSocket.sendto('FIN'.encode(), message.clientAddress)
        


def send_file(file, serverSocket, clientAddress, queue):
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

    # Inform the client that the download is finished
    serverSocket.sendto("FIN".encode(), clientAddress)
    logging.debug(f"Sent FIN to client {clientAddress}")

    logging.info(f"Sent file to client {clientAddress}")


def handle_upload_request(clientAddress, serverSocket, queue, dirpath, filename):
    logging.info("Handling upload request")

    # Send filename received ACK.
    serverSocket.sendto('ACK Filename received.'.encode(), clientAddress)
    logging.debug(f"ACK filename received sent to client {clientAddress}")

    # Create new file where to put the content of the file to receive.
    # Opens a file for writing. Creates a new file if it does not exist
    # or truncates the file if it exists.
    file = open(dirpath + filename, 'wb')
    logging.debug(f"File to write in is {dirpath}/{filename}")

    recv_file(file, serverSocket, queue)

    file.close()

def handle_download_request(clientAddress, serverSocket, queue, dirpath, filename):
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

    send_file(file, serverSocket, clientAddress, queue)

    file.close()


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
