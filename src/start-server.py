import argparse
from socket import socket, AF_INET, SOCK_DGRAM
import os
from StopAndWait import *
from UDPHandler import *


DEFAULT_SERVER_IP = '127.0.0.1'
DEFAULT_SERVER_PORT = 12000
BUFSIZE = 2048
DEFAULT_DIRPATH = 'files/'
DEFAULT_LOGGING_LEVEL = logging.INFO
UPLOAD = "upload"
DOWNLOAD = "downloads"
TIMEOUT=2
def process_first_message(encodedFirstMessage):
    firstMessage = encodedFirstMessage.decode().split()
    return (firstMessage[0], firstMessage[1])

def handle_upload_request(serverSocket, stopAndWait, clientAddress, filename, lastBit):
    logging.info("Handling upload request")

    # Send received ACK.
    send(serverSocket, lastBit, 'ACK'.encode(), clientAddress)
    logging.debug(f"ACK filename received sent to client {clientAddress}")

    # Create new file where to put the content of the file to receive.
    # Opens a file for writing. Creates a new file if it does not exist
    # or truncates the file if it exists.
    file = open(dirpath + filename, 'wb')
    logging.debug(f"File to write in is {dirpath}/{filename}")
    lastBit, maybeFileContent, address = stopAndWait.receive(clientAddress, lastSentMsg='ACK'.encode(), lastRcvBit=lastBit)

    while maybeFileContent != "FIN".encode():
        logging.debug(
            f"Received file content from {address}")

        # Write file content to new file
        file.write(maybeFileContent)
        logging.debug("File content written")

        # Send file content received ACK.
        send(serverSocket, lastBit, 'ACK'.encode(), address)
        logging.debug(f"ACK sent to {address}")
        lastBit, maybeFileContent, address = stopAndWait.receive(clientAddress, lastSentMsg='ACK'.encode(),lastRcvBit=lastBit)
    send(serverSocket, lastBit, 'FIN_ACK'.encode(), address)
    logging.debug(f"FIN_ACK sent to client {clientAddress}")
    logging.info(f"Received file from client {clientAddress}")

    file.close()


def handle_download_request(serverSocket, stopAndWait, clientAddress, filename, lastBit):
    logging.info("Handling downloads request")

    if not os.path.exists(dirpath + filename):
        logging.error(f"File does not exist: {dirpath}/{filename}")
        # Send filename does not exist NAK.
        send(serverSocket, lastBit, 'FIN'.encode(), clientAddress)
        logging.debug(
            f"Sending FIN: File does not exist to client {clientAddress}")
        return

    # Send filename received ACK.
    send(serverSocket, lastBit, 'ACK'.encode(), clientAddress)
    stopAndWait.alternateBit()
    logging.debug(
        f"ACK Filename received sent to client {clientAddress}")

    file = open(dirpath + filename, 'rb')
    logging.debug(f"File to read from is {dirpath}/{filename}")

    try:
        data = file.read(BUFSIZE)

        while data:
            logging.debug("Read data from file")
            send(serverSocket, stopAndWait.bit, data, clientAddress)
            _, message, _ = stopAndWait.receive(clientAddress, lastSentMsg=data, lastSentBit=stopAndWait.bit,
                                                timeout=TIMEOUT)
            stopAndWait.alternateBit()
            if message != "ACK".encode():
                if message == "FIN".encode():
                    logging.info(f"FIN messsage received.")
                    send(serverSocket, stopAndWait.bit, "FIN_ACK".encode(), clientAddress)
                else:
                    logging.error(f"Unknown message received {message.decode()}")
                    send(serverSocket, stopAndWait.bit, "FIN".encode(), clientAddress)
                return
            data = file.read(BUFSIZE)
        # TODO: FIX THIS BUG! Think about what we have to do if END is never received
        send(serverSocket, stopAndWait.bit, "FIN".encode(), clientAddress)
        _, message, _ = stopAndWait.receive(clientAddress, lastSentMsg="FIN".encode(), lastSentBit=stopAndWait.bit,
                                            timeout=TIMEOUT)
        logging.debug("Sent FIN to client")
        logging.info("File sent to client")
    except BaseException as err:
        logging.error(
            f"An error occurred when sending file to client: {format(err)}")
    finally:
        # Close everything
        file.close()


def listen(serverSocket):
    logging.info("Socket created and listening for requests")

    while True:
        stopAndWait = StopAndWait(serverSocket)
        bit, firstMessage, clientAddress = stopAndWait.receive()

        logging.debug(f"First message received from {clientAddress}")
        logging.debug(f"First message content: {firstMessage}")
        (command, filename) = process_first_message(firstMessage)
        logging.info(f"Received {command} command for file {filename}")

        # TODO: Handle case where command is not upload and downloads
        if command == UPLOAD:
            handle_upload_request(serverSocket, stopAndWait, clientAddress, filename, bit)
        elif command == DOWNLOAD:
            handle_download_request(serverSocket, stopAndWait, clientAddress, filename, bit)
        else:
            logging.error(
                f"Received an invalid command from client {clientAddress}")
        break

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
