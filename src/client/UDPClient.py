from socket import *
import sys

serverName = ''
serverPort = 12000
bufsize = 2048

COMMAND = None
FILEPATH = ''
FILENAME = None

def get_filename(filepath):
    return filepath.split('/')[-1]

def give_help():

    if COMMAND == 'upload':
        print("Usage: upload [-h] [-s FILEPATH] [-s FILENAME]")
        print()
        print("Optional arguments:")
        print(" -h    show this help message and exit")
        print(" -s    source file path")
        print(" -n    file name")
    elif COMMAND == 'download':
        print("Usage: download [-h] [-s FILEPATH] [-s FILENAME]")
        print()
        print("Optional arguments:")
        print(" -h    show this help message and exit")
        print(" -s    destination file path")
        print(" -n    file name")
    else:
        print("Usage: [upload | download] [-h] [-s FILEPATH] [-s FILENAME]")
        print()
        print("Optional arguments:")
        print(" -h    show this help message and exit")
        print(" -s    source | destination file path")
        print(" -n    file name")


def send_filename(clientSocket):
    clientSocket.sendto((COMMAND + ' ' + FILENAME).encode(), (serverName, serverPort))
    modifiedMessage, serverAddress = clientSocket.recvfrom(bufsize)
    print(modifiedMessage.decode())


def send_file(file, clientSocket):
    data = file.read(bufsize)

    while data:
        clientSocket.sendto(data,(serverName, serverPort))
        message, serverAddress = clientSocket.recvfrom(bufsize)

        if message.decode() != 'ACK':
            print("Ha ocurrido un error")
            break

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

    send_filename(clientSocket)

    # Open file for sending using byte-array option.
    file = open(FILEPATH + FILENAME, "rb")

    send_file(file, clientSocket)

    # Close everything
    file.close()

def handle_download_request(clientSocket):

    send_filename(clientSocket)

    # Open file for sending using byte-array option.
    file = open(FILEPATH + FILENAME, "wb")

    recv_file(file, clientSocket)

    # Close everything
    file.close()

def start_client():

    global COMMAND
    global FILEPATH
    global FILENAME

    sys.argv.pop(0)
    
    while sys.argv:
        expected_flag = sys.argv.pop(0)

        if expected_flag == '-h':
            give_help()
            return
        elif expected_flag in ['upload', 'download']:
            COMMAND = expected_flag
        elif expected_flag == '-s':
            FILEPATH = sys.argv.pop(0) + '/'
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

