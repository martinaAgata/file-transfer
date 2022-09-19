from socket import *
import os

serverPort = 12000
bufsize = 2048
DIRPATH = 'files/'

def process_first_message(encodedFirstMessage):

    firstMessage = encodedFirstMessage.decode().split()

    return (firstMessage[0], firstMessage[1])

def recv_file(file, serverSocket):
    # Receive file content.
    maybeFileContent, clientAddress = serverSocket.recvfrom(bufsize)

    #TODO: Think about a better way to end the transfer
    while maybeFileContent != "END".encode():

        # Write file content to new file
        file.write(maybeFileContent)

        # Send file content received ACK.
        serverSocket.sendto('ACK'.encode(), clientAddress)
        maybeFileContent, clientAddress = serverSocket.recvfrom(bufsize)


    print('Received file content from the Client.')

def send_file(file, serverSocket, clientAddress):
    data = file.read(bufsize)

    while data:
        serverSocket.sendto(data, clientAddress)
        message, serverAddress = serverSocket.recvfrom(bufsize)

        if message.decode() != 'ACK':
            print("An error has occurred")
            break

        data = file.read(bufsize)

    # inform the server that the download is finished
    serverSocket.sendto("END".encode(), clientAddress)

def handle_upload_request(serverSocket, clientAddress, filename):

    # Send filename received ACK.
    serverSocket.sendto('ACK Filename received.'.encode(), clientAddress)

    # Create new file where to put the content of the file to receive.
    # Opens a file for writing. Creates a new file if it does not exist or truncates the file if it exists.
    file = open(DIRPATH + filename, 'wb')

    recv_file(file, serverSocket)

    file.close()
    
def handle_download_request(serverSocket, clientAddress, filename):

    if not os.path.exists(DIRPATH + filename):
        # Send filename does not exist NAK.
        serverSocket.sendto('NAK File does not exist.'.encode(), clientAddress)
        return
    
    # Send filename received ACK.
    serverSocket.sendto('ACK Filename received.'.encode(), clientAddress)

    file = open(DIRPATH + filename, 'rb')

    send_file(file, serverSocket, clientAddress)

    file.close()

def listen(serverSocket):
    print('The server is ready to receive')

    while True:
        # Receive filepath first.
        firstMessage, clientAddress = serverSocket.recvfrom(bufsize)

        (command, filename) = process_first_message(firstMessage)
        print('Filename: ' + filename)

        #TODO: Handle case where command is not upload and download 
        if command == 'upload':
            handle_upload_request(serverSocket, clientAddress, filename)
        else:
            handle_download_request(serverSocket, clientAddress, filename)
            
def start_server():
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))

    # Create /files directory if not exist
    if not os.path.isdir('files'):
        os.mkdir('files')

    listen(serverSocket)

    serverSocket.close()


def main():
    start_server()

if __name__ == "__main__":
    main()



