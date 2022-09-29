import argparse
from socket import socket, AF_INET, SOCK_DGRAM
import os
from client_handler import ClientHandler
from message import Message

import sys
sys.path.append('..')
from definitions import *


# def process_first_message(encodedFirstMessage):

#     firstMessage = encodedFirstMessage.decode().split()

#     return (firstMessage[0], firstMessage[1])


# def recv_file(file, serverSocket):
#     # Receive file content.
#     maybeFileContent, clientAddress = serverSocket.recvfrom(BUFSIZE)

#     # TODO: Think about a better way to end the transfer
#     while maybeFileContent != "END".encode():
#         logging.debug(
#             f"Received file content from client {clientAddress}")

#         # Write file content to new file
#         file.write(maybeFileContent)
#         logging.debug("File content written")

#         # Send file content received ACK.
#         serverSocket.sendto('ACK'.encode(), clientAddress)
#         logging.debug(f"ACK sent to client {clientAddress}")

#         maybeFileContent, clientAddress = serverSocket.recvfrom(BUFSIZE)

#     logging.info(f"Received file from client {clientAddress}")


# def send_file(file, serverSocket, clientAddress):
#     data = file.read(BUFSIZE)

#     while data:
#         logging.debug("Read data from file")
#         serverSocket.sendto(data, clientAddress)
#         logging.debug(f"Sent data to client {clientAddress}")

#         message, serverAddress = serverSocket.recvfrom(BUFSIZE)
#         logging.debug(
#             f"Received message {message} from client {clientAddress}")

#         if message.decode() != 'ACK':
#             logging.error(f"ACK not received from client {clientAddress}")
#             break  # TODO: wouldn't it be a return instead of a break?

#         data = file.read(BUFSIZE)

#     # inform the client that the download is finished
#     serverSocket.sendto("FIN".encode(), clientAddress)
#     logging.debug(f"Sent FIN to client {clientAddress}")

#     logging.info(f"Sent file to client {clientAddress}")


# def handle_upload_request(serverSocket, clientAddress, filename):
#     logging.info("Handling upload request")

#     # Send filename received ACK.
#     serverSocket.sendto('ACK Filename received.'.encode(), clientAddress)
#     logging.debug(f"ACK filename received sent to client {clientAddress}")

#     # Create new file where to put the content of the file to receive.
#     # Opens a file for writing. Creates a new file if it does not exist
#     # or truncates the file if it exists.
#     file = open(dirpath + filename, 'wb')
#     logging.debug(f"File to write in is {dirpath}/{filename}")

#     recv_file(file, serverSocket)

#     file.close()


# def handle_download_request(serverSocket, clientAddress, filename):
#     logging.info("Handling download request")

#     if not os.path.exists(dirpath + filename):
#         logging.error(f"File does not exist: {dirpath}/{filename}")
#         # Send filename does not exist NAK.
#         serverSocket.sendto('NAK File does not exist.'.encode(), clientAddress)
#         logging.debug(
#             f"Sending NAK File does not exist to client {clientAddress}")
#         return

#     # Send filename received ACK.
#     serverSocket.sendto('ACK Filename received.'.encode(), clientAddress)
#     logging.debug(
#         f"ACK Filename received sent to client {clientAddress}")

#     file = open(dirpath + filename, 'rb')
#     logging.debug(f"File to read from is {dirpath}/{filename}")

#     send_file(file, serverSocket, clientAddress)

#     file.close()


def listen(serverSocket):
    logging.info("Socket created and listening for requests")

    clientHandler = None
    clientsDict = {}

    while True:
        # Receive filepath first.
        firstMessage, clientAddress = serverSocket.recvfrom(BUFSIZE)

        # IGNORE
        logging.debug(f"First message received from {clientAddress}")
        logging.debug(f"First message content: {firstMessage.decode()}")
        (command, filename) = process_first_message(firstMessage)
        logging.info(f"Received {command} command for file {filename}")
        message = Message(firstMessage, clientAddress)

        if clientsDict.contains(clientAddress):
            # OLD CLIENT
            clientHandler = clientsDict[clientAddress]
        else:
            # NEW CLIENT
            # TODO: maybe check if file exists or NAK
            if message.type in [UPLOAD, DOWNLOAD]:
                clientHandler = ClientHandler(clientAddress, serverSocket, dirpath)
                clientHandler.start_thread()
                clientsDict[clientAddress] = clientHandler
            else:
                # TODO: log me
                # TODO: send reasons for NAK 
                serverSocket.sendto("NAK".encode(), clientAddress)
                continue

        clientHandler.send(message)

        # TODO: Check that every time that a FIN is send, the thread go to the
        # end of the scope.
        #
        # If it is FIN -> Join client, and send FIN_ACK
        # If it is FIN_ACK -> We already have sent FIN, so just join client
        if message.type in [FIN, FIN_ACK]:
            clientHandler.join(timeout=4)

        # TODO: Handle case where command is not upload and download
        # if command == UPLOAD:
        #     handle_upload_request(serverSocket, clientAddress, filename)
        # elif command == DOWNLOAD:
        #     handle_download_request(serverSocket, clientAddress, filename)
        # else:
        #     logging.error(
        #         f"Received an invalid command from client {clientAddress}")


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
    global dirpath
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

    listen(serverSocket)

    serverSocket.close()
    logging.info("Socket closed")


def main():
    start_server()


if __name__ == "__main__":
    main()
