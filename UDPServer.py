from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print('The server is ready to receive')

# Receive filename first.
filename, clientAddress = serverSocket.recvfrom(2048)
filename = filename.decode()
print('Filename: ' + filename)

# Send filename received ACK.
serverSocket.sendto('Filename received.'.encode(), clientAddress)

# Create new file where to put the content of the file to receive.
# Opens a file for writing. Creates a new file if it does not exist or truncates the file if it exists.
file = open('copy-of-' + filename, 'w')

# Receive file content.
fileContent, clientAddress = serverSocket.recvfrom(2**30)
print('Received file content from the Client.')

# Send file content received ACK.
serverSocket.sendto('File content received by the server.'.encode(), clientAddress)

# Write file content to new file
file.write(fileContent.decode())

file.close()
serverSocket.close()