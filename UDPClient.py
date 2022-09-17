from socket import *

serverName = ''
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

message = input('Input filename: ')

# Send filename.
clientSocket.sendto(message.encode(), (serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())

# Open file for sending using byte-array option.
file = open(message, "rb")
data = file.read()

# Send file content.
clientSocket.sendto(data,(serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())

file.close()
clientSocket.close()