import argparse
from socket import socket, AF_INET, SOCK_DGRAM
import os

DEFAULT_SERVER_IP = '127.0.0.1'
DEFAULT_SERVER_PORT = 12000
BUFSIZE = 2048
DEFAULT_DIRPATH = 'files/'


def process_first_message(encodedFirstMessage):

    firstMessage = encodedFirstMessage.decode().split()

    return (firstMessage[0], firstMessage[1])


def recv_file(file, serverSocket):
    # Receive file content.
    maybeFileContent, clientAddress = serverSocket.recvfrom(BUFSIZE)

    # TODO: Think about a better way to end the transfer
    while maybeFileContent != "END".encode():

        # Write file content to new file
        file.write(maybeFileContent)

        # Send file content received ACK.
        serverSocket.sendto('ACK'.encode(), clientAddress)
        maybeFileContent, clientAddress = serverSocket.recvfrom(BUFSIZE)

    print('Received file content from the Client.')


def send_file(file, serverSocket, clientAddress):
    data = file.read(BUFSIZE)

    while data:
        serverSocket.sendto(data, clientAddress)
        message, serverAddress = serverSocket.recvfrom(BUFSIZE)

        if message.decode() != 'ACK':
            print("An error has occurred")
            break

        data = file.read(BUFSIZE)

    # inform the server that the download is finished
    serverSocket.sendto("END".encode(), clientAddress)


def handle_upload_request(serverSocket, clientAddress, filename):

    # Send filename received ACK.
    serverSocket.sendto('ACK Filename received.'.encode(), clientAddress)

    # Create new file where to put the content of the file to receive.
    # Opens a file for writing. Creates a new file if it does not exist
    # or truncates the file if it exists.
    file = open(dirpath + filename, 'wb')

    recv_file(file, serverSocket)

    file.close()


def handle_download_request(serverSocket, clientAddress, filename):

    if not os.path.exists(dirpath + filename):
        # Send filename does not exist NAK.
        serverSocket.sendto('NAK File does not exist.'.encode(), clientAddress)
        return

    # Send filename received ACK.
    serverSocket.sendto('ACK Filename received.'.encode(), clientAddress)

    file = open(dirpath + filename, 'rb')

    send_file(file, serverSocket, clientAddress)

    file.close()


def listen(serverSocket):
    print('The server is ready to receive')

    while True:
        # Receive filepath first.
        firstMessage, clientAddress = serverSocket.recvfrom(BUFSIZE)

        (command, filename) = process_first_message(firstMessage)
        print('Filename: ' + filename)

        # TODO: Handle case where command is not upload and download
        if command == 'upload':
            handle_upload_request(serverSocket, clientAddress, filename)
        else:
            handle_download_request(serverSocket, clientAddress, filename)


def parse_arguments():
    argParser = argparse.ArgumentParser(
        prog='start-server',
        description='Start the server with a specific configuration')

    group = argParser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose',
                       help='increase output verbosity', action='store_true')
    group.add_argument('-q', '--quiet',
                       help='decrease output verbosity', action='store_true')

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

    print("verbose", args.verbose)
    print("quiet", args.quiet)
    host = args.host
    print("host", host)
    port = args.port
    print("port", port)
    global dirpath
    dirpath = args.storage
    print("storage", dirpath)

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((host, port))

    # Create /files directory if not exist
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)

    listen(serverSocket)

    serverSocket.close()


def main():
    start_server()


if __name__ == "__main__":
    main()
