import logging
from lib.definitions import ACK, DATA, FIN, FIN_ACK


def handle(clientAddress, serverSocket, queue, dirpath, filename):
    logging.info("Handling upload request")

    # Send filename received ACK.
    serverSocket.sendto(f'{ACK} Filename received.'.encode(), clientAddress)
    logging.debug(f"{ACK} filename received sent to client {clientAddress}")

    # Create new file where to put the content of the file to receive.
    # Opens a file for writing. Creates a new file if it does not exist
    # or truncates the file if it exists.
    file = open(dirpath + filename, 'wb')
    logging.debug(f"File to write in is at {dirpath}{filename}")

    recv_file(file, serverSocket, queue)

    file.close()


def recv_file(file, serverSocket, queue):
    # Receive file content (should be first packet).
    message = queue.get()

    # TODO: Think about a better way to end the transfer.
    # TODO: Perhaps it could stop iterating if type IS NOT DATA.
    while message.type == DATA:
        logging.debug(f"Received file content from client {message.clientAddress}")

        # Write file content to new file (it should already be encoded)
        file.write(message.data)
        logging.debug("File content written")

        # Send file content received ACK.
        serverSocket.sendto('ACK'.encode(), message.clientAddress)
        logging.debug(f"ACK sent to client {message.clientAddress}")

        message = queue.get()

    if message.type == FIN:
        logging.info(f"Received file from client {message.clientAddress}")
        serverSocket.sendto(FIN_ACK.encode(), message.clientAddress)
    else:
        logging.info(
            f"ERROR: Received a {message.type} packet at the end" "of file upload"
        )
        # TODO: Check if sending FIN is the best choice to close the client.
        serverSocket.sendto(FIN.encode(), message.clientAddress)
