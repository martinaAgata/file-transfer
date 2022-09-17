from socket import *
import sys

serverName = ''
serverPort = 12000
bufsize = 2048

def user_ask_for_help():
    return (len(sys.argv) == 2) and (sys.argv[1] == '-h')

def give_help():
    print("Usage: [-h] [-s FILEPATH]")
    print()
    print("Optional arguments:")
    print(" -h    show this help message and exit")
    print(" -s    source file path")


def user_give_filepath():
    return (len(sys.argv) == 3) and (sys.argv[1] == '-s')

def get_path():
    return sys.argv[2]

def send_filepath(path, clientSocket):

    # Send filename.
    clientSocket.sendto(path.encode(), (serverName, serverPort))
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


def start_client():

    if user_ask_for_help():
        give_help()
        return
    elif user_give_filepath():
        filepath = get_path()
    else:
        print("Wrong number of arguments")
        return

    clientSocket = socket(AF_INET, SOCK_DGRAM)

    
    send_filepath(filepath, clientSocket)

    # Open file for sending using byte-array option.
    file = open(filepath, "rb")
    send_file_content(file, clientSocket)

    # Close everything

    file.close()
    clientSocket.close()

def main():
    start_client()

if __name__ == "__main__":
    main()

