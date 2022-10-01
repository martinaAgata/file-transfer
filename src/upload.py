import argparse
from socket import socket, AF_INET, SOCK_DGRAM
import os
from StopAndWait import *
import traceback

DEFAULT_SERVER_IP = '127.0.0.1'
DEFAULT_SERVER_PORT = 12000
BUFSIZE = 2048
DEFAULT_UPLOAD_FILEPATH = 'lib/resources/'
DEFAULT_LOGGING_LEVEL = logging.INFO
TIMEOUT=2

def handle_upload_request(clientSocket):
    logging.info("Handling upload")

    if not os.path.exists(filepath + filename):
        logging.error(
            f"Requested source file {filepath}/{filename} does not exists")
        return

    stopAndWait = StopAndWait(clientSocket)
    uploadCmd = ('upload' + ' ' + filename).encode()
    send(clientSocket, stopAndWait.bit, uploadCmd, serverIP, port)
    _, message, _ = stopAndWait.receive((serverIP, port), lastSentMsg=uploadCmd, lastSentBit=stopAndWait.bit, timeout= TIMEOUT)
    stopAndWait.alternateBit()
    if message != "ACK".encode():
        if message == "FIN".encode():
            send(clientSocket, stopAndWait.bit, "FIN_ACK".encode(), serverIP, port)
        else:
            send(clientSocket, stopAndWait.bit, "FIN".encode(), serverIP, port)
        return


    # Open file for sending using byte-array option.
    file = open(filepath + filename, "rb")

    try:
        data = file.read(BUFSIZE)

        while data:
            logging.debug("Read data from file")
            send(clientSocket, stopAndWait.bit, data, serverIP, port)
            _, message,_ = stopAndWait.receive((serverIP, port), lastSentMsg=data, lastSentBit=stopAndWait.bit,
                                timeout=TIMEOUT)
            stopAndWait.alternateBit()
            if message != "ACK".encode():
                if message == "FIN".encode():
                    send(clientSocket, stopAndWait.bit, "FIN_ACK".encode(), serverIP, port)
                else:
                    send(clientSocket, stopAndWait.bit, "FIN".encode(), serverIP, port)
                return
            data = file.read(BUFSIZE)
        # TODO: FIX THIS BUG! Think about what we have to do if END is never received
        send(clientSocket, stopAndWait.bit, "FIN".encode(), serverIP, port)
        _ , message, _ = stopAndWait.receive((serverIP, port), lastSentMsg="FIN".encode(), lastSentBit=stopAndWait.bit,
                            timeout=TIMEOUT)
        logging.debug("Sent FIN to server")
        logging.info("File sent to server")
    except BaseException as err:
        logging.error(
            f"An error occurred when sending file to server: {format(err)}")
    finally:
        # Close everything
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

    logging.debug(f"Server IP address: {serverIP}")
    logging.debug(f"Server port: {port}")
    logging.debug(f"Filepath: {filepath}")
    logging.debug(f"Filename: {filename}")

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    # TODO: we need to check this? 4 is an arbitrary value
    clientSocket.settimeout(4)

    handle_upload_request(clientSocket)
    clientSocket.close()
    logging.debug(f"Socket {clientSocket} closed")


def main():
    start_client()


if __name__ == "__main__":
    main()
