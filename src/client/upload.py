import argparse
from socket import socket, AF_INET, SOCK_DGRAM
import os

DEFAULT_SERVER_IP = '127.0.0.1'
DEFAULT_SERVER_PORT = 12000
BUFSIZE = 2048
DEFAULT_UPLOAD_FILEPATH = '../../resources/'


# TODO: delete duplicated coed upload.py-download.py (is_ack, send_filename)


# Splits message into [ACK | NAK] + data
def is_ack(message):
    splited_message = message.decode().split(" ", 1)
    status = splited_message[0]

    response = ''
    if len(splited_message) == 2:
        response = splited_message[1]

    if status == 'ACK':
        return (True, response)
    elif status == 'NAK':
        return (False, response)
    else:
        return (False, "Unknown acknowledge: " + message.decode())


def send_filename(clientSocket):
    clientSocket.sendto(('upload' + ' ' + filename).encode(),
                        (serverIP, port))
    message, _ = clientSocket.recvfrom(BUFSIZE)

    (ack, response) = is_ack(message)

    if not ack:
        raise NameError(response)


def send_file(file, clientSocket):
    data = file.read(BUFSIZE)

    while data:

        clientSocket.sendto(data, (serverIP, port))
        message, serverAddress = clientSocket.recvfrom(BUFSIZE)
        (ack, response) = is_ack(message)

        if not ack:
            # TODO: Think a better error
            raise BaseException(response)

        data = file.read(BUFSIZE)

    # Inform the server that the download is finished
    clientSocket.sendto("END".encode(), (serverIP, port))


def handle_upload_request(clientSocket):

    if not os.path.exists(filepath + filename):
        print("Requested source file does not exists")
        return

    try:
        send_filename(clientSocket)
    except NameError as err:
        print("Server: " + format(err))
        return

    # Open file for sending using byte-array option.
    file = open(filepath + filename, "rb")

    try:
        send_file(file, clientSocket)
    except BaseException as err:
        print("Server: " + format(err))
    finally:
        # Close everything
        file.close()


def parse_arguments():
    argParser = argparse.ArgumentParser(
        prog='upload', description='Upload a file to a given server')

    group = argParser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose',
                       help='increase output verbosity', action='store_true')
    group.add_argument('-q', '--quiet',
                       help='decrease output verbosity', action='store_true')

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

    print("verbose", args.verbose)
    print("quiet", args.quiet)
    global serverIP
    serverIP = args.host
    print("host", serverIP)
    global port
    port = args.port
    print("port", port)
    global filepath
    filepath = args.src
    print("filepath", filepath)
    global filename
    filename = args.name
    print("filename", filename)

    clientSocket = socket(AF_INET, SOCK_DGRAM)

    handle_upload_request(clientSocket)

    clientSocket.close()


def main():
    start_client()


if __name__ == "__main__":
    main()
