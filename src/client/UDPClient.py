from socket import *
import sys

serverName = ''
serverPort = 12000
bufsize = 2048

def get_filename(filepath):
    return filepath.split('/')[-1]

def give_help():
    print("Usage: [upload | download] [-h] [-s FILEPATH]")
    print()
    print("Optional arguments:")
    print(" -h    show this help message and exit")
    print(" -s    source file path")

def send_filename(name, clientSocket):
    clientSocket.sendto(('upload ' + name).encode(), (serverName, serverPort))
    modifiedMessage, serverAddress = clientSocket.recvfrom(bufsize)
    print(modifiedMessage.decode())


def send_file_content(file, clientSocket):
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

def handle_upload_request(clientSocket, filepath):

    send_filename(get_filename(filepath), clientSocket)

    # Open file for sending using byte-array option.
    file = open(filepath, "rb")

    send_file_content(file, clientSocket)

    # Close everything
    file.close()


def start_client():

    sys.argv.pop(0)
    command = None
    filepath = None
    
    while sys.argv:
        expected_flag = sys.argv.pop(0)

        if expected_flag == '-h':
            give_help()
            return
        elif expected_flag == '-s':
            filepath = sys.argv.pop(0)
        elif expected_flag in ['upload', 'download']:
            command = expected_flag
        else:
            print("Something gone wrong with the arguments. Type '[upload | download] -h' for help")
            return

    if command == None:
        print("Missed command. Type '[upload | download] -h' for help")
        return

    clientSocket = socket(AF_INET, SOCK_DGRAM)

    if command == 'upload':
        handle_upload_request(clientSocket, filepath)
    else:
        # Case: download_request()
        print("THIS FEATURE IS UNDER DEVELOPMENT. COME BACK SOON XD")


    clientSocket.close()

def main():
    start_client()

if __name__ == "__main__":
    main()

