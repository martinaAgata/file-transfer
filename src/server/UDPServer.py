from socket import *
import os

serverPort = 12000
bufsize = 2048
DIRPATH = 'files/'

def get_filename(filepath):
    return filepath.split('/')[-1]

def process_first_message(encodedFirstMessage):

    firstMessage = encodedFirstMessage.decode().split()

    return (firstMessage[0], firstMessage[1])

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

def handle_upload_request(serverSocket, filename):

    # Create new file where to put the content of the file to receive.
    # Opens a file for writing. Creates a new file if it does not exist or truncates the file if it exists.
    file = open(DIRPATH + filename, 'wb')

    recv_file(file, serverSocket)

    file.close()
    
def handle_download_request(serverSocket, clientAddress):
    serverSocket.sendto('THIS FEATURE IS UNDER DEVELOPMENT. COME BACK SOON XD'.encode(), clientAddress)

def listen(serverSocket):
    print('The server is ready to receive')

    while True:
        # Receive filepath first.
        firstMessage, clientAddress = serverSocket.recvfrom(bufsize)

        (command, filename) = firstMessage.decode().split()
        print('Filename: ' + filename)
        
        # TODO: Must check that is UPLOAD or DOWNLOAD
        if command == 'upload':
            # Send filename received ACK.
            serverSocket.sendto('Filename received.'.encode(), clientAddress)
            handle_upload_request(serverSocket, filename)
        else:
            handle_download_request(serverSocket, clientAddress)


        

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



