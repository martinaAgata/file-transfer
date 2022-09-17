from socket import *

serverPort = 12000
bufsize = 2048

def get_filename(filepath):
    return filepath.split('/')[-1]

def recv_file(file, serverSocket):
    # Receive file content.
    maybeFileContent, clientAddress = serverSocket.recvfrom(bufsize)

    while maybeFileContent != "FIN".encode():

        # Write file content to new file
        file.write(maybeFileContent)

        # Send file content received ACK.
        serverSocket.sendto('ACK'.encode(), clientAddress)
        maybeFileContent, clientAddress = serverSocket.recvfrom(bufsize)


    print('Received file content from the Client.')


def listen(serverSocket):
    print('The server is ready to receive')

    # Receive filepath first.
    filepath, clientAddress = serverSocket.recvfrom(bufsize)
    filepath = filepath.decode()
    print('Filepath: ' + filepath)

    # Send filename received ACK.
    serverSocket.sendto('Filename received.'.encode(), clientAddress)

    # Create new file where to put the content of the file to receive.
    # Opens a file for writing. Creates a new file if it does not exist or truncates the file if it exists.
    file = open('files/' + get_filename(filepath), 'wb')

    recv_file(file, serverSocket)

    file.close()

def start_server():
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))

    listen(serverSocket)

    serverSocket.close()


def main():
    start_server()

if __name__ == "__main__":
    main()


