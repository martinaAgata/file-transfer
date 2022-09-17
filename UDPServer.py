from socket import *

serverPort = 12000
bufsize = 2048

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

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print('The server is ready to receive')

# Receive filename first.
filename, clientAddress = serverSocket.recvfrom(bufsize)
filename = filename.decode()
print('Filename: ' + filename)

# Send filename received ACK.
serverSocket.sendto('Filename received.'.encode(), clientAddress)

# Create new file where to put the content of the file to receive.
# Opens a file for writing. Creates a new file if it does not exist or truncates the file if it exists.
file = open('copy-of-' + filename, 'wb')

recv_file(file, serverSocket)

file.close()
serverSocket.close()