from socket import *

serverName = ''
serverPort = 12000
bufsize = 2048

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


clientSocket = socket(AF_INET, SOCK_DGRAM)

message = input('Input filename: ')

# Send filename.
clientSocket.sendto(message.encode(), (serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(bufsize)
print(modifiedMessage.decode())

# Open file for sending using byte-array option.
file = open(message, "rb")

send_file(file, clientSocket)

# Close everything

file.close()
clientSocket.close()