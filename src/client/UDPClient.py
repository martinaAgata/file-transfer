from lib2to3.pytree import Base
from socket import *
import sys
import os

serverName = ''
serverPort = 12000
bufsize = 2048

COMMAND = None
DOWNLOAD_FILEPATH = '../../downloads/'
UPLOAD_FILEPATH = '../../resources/'
FILENAME = None

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
        return (False, "Unknown acknowledge: " + message)

def give_help():

    if COMMAND == 'upload':
        print("Usage: upload [-h] [-s FILEPATH] [-n FILENAME]")
        print()
        print("Optional arguments:")
        print(" -h    show this help message and exit")
        print(" -s    source file path")
        print(" -n    file name")
    elif COMMAND == 'download':
        print("Usage: download [-h] [-s FILEPATH] [-n FILENAME]")
        print()
        print("Optional arguments:")
        print(" -h    show this help message and exit")
        print(" -s    destination file path")
        print(" -n    file name")
    else:
        print("Usage: [upload | download] [-h] [-s FILEPATH] [-n FILENAME]")
        print()
        print("Optional arguments:")
        print(" -h    show this help message and exit")
        print(" -s    source | destination file path")
        print(" -n    file name")


def send_filename(clientSocket):
    clientSocket.sendto((COMMAND + ' ' + FILENAME).encode(), (serverName, serverPort))
    message, _ = clientSocket.recvfrom(bufsize)

    (ack, response) = is_ack(message)
    
    if not ack:
        raise NameError(response)


def send_file(file, clientSocket):
    data = file.read(bufsize)

    while data:
        
        clientSocket.sendto(data,(serverName, serverPort))
        message, serverAddress = clientSocket.recvfrom(bufsize)
        (ack, response) = is_ack(message)

        if not ack:
            raise BaseException(response)

        data = file.read(bufsize)

    # inform the server that the download is finished
    clientSocket.sendto("FIN".encode(),(serverName, serverPort))

def recv_file(file, clientSocket):
    # Receive file content.
    maybeFileContent, serverAddress = clientSocket.recvfrom(bufsize)

    while maybeFileContent != "FIN".encode():

        # Write file content to new file
        file.write(maybeFileContent)

        # Send file content received ACK.
        clientSocket.sendto('ACK'.encode(), serverAddress)
        maybeFileContent, serverAddress = clientSocket.recvfrom(bufsize)


    print('Received file content from the Server.')


def handle_upload_request(clientSocket):

    if not os.path.exists(UPLOAD_FILEPATH + FILENAME):
        print("Requested source file does not exists")
        return

    try:
        send_filename(clientSocket)
    except NameError as err:
        print("Server: " + format(err))
        return

    # Open file for sending using byte-array option.
    file = open(UPLOAD_FILEPATH + FILENAME, "rb")

    try:
        send_file(file, clientSocket)
    except BaseException as err:
        print("Server: " + format(err))
    finally:
        # Close everything
        file.close()



def handle_download_request(clientSocket):

    if not os.path.exists(DOWNLOAD_FILEPATH):
        print("Requested destination filepath does not exists")
        return

    try:
        send_filename(clientSocket)
    except NameError as err:
        print("Server: " + format(err))
        return

    # Open file for sending using byte-array option.
    # If file does not exist, then creates a new one.
    file = open(DOWNLOAD_FILEPATH + FILENAME, "wb")

    try:
        recv_file(file, clientSocket)
    except BaseException as err:
        print("Server: " + format(err))
    finally:
        # Close everything
        file.close()

def start_client():

    global COMMAND
    global UPLOAD_FILEPATH
    global DOWNLOAD_FILEPATH
    global FILENAME

    sys.argv.pop(0)
    
    # TODO: hacer que no crashee xd
    while sys.argv:
        expected_flag = sys.argv.pop(0)

        if expected_flag == '-h':
            give_help()
            return
        elif expected_flag in ['upload', 'download']:
            COMMAND = expected_flag
        elif expected_flag == '-s':
            if COMMAND == 'upload':
                UPLOAD_FILEPATH = sys.argv.pop(0) + '/'
            else:
                DOWNLOAD_FILEPATH = sys.argv.pop(0) + '/'
        elif expected_flag == '-n':
            FILENAME = sys.argv.pop(0)
        else:
            print("Something gone wrong with the arguments. Type '[upload | download] -h' for help")
            return

    if COMMAND == None:
        print("Missed command. Type '[upload | download] -h' for help")
        return

    clientSocket = socket(AF_INET, SOCK_DGRAM)

    if COMMAND == 'upload':
        handle_upload_request(clientSocket)
    else:
        handle_download_request(clientSocket)


    clientSocket.close()

def main():
    start_client()

if __name__ == "__main__":
    main()

