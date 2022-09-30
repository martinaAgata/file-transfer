import logging
import os
from .definitions import (BUFSIZE, UPLOAD, DOWNLOAD, DATA,
                          FIN, FIN_ACK, ACK, NAK)


def process_first_message(encodedFirstMessage):
    firstMessage = encodedFirstMessage.decode().split()
    return (firstMessage[0], firstMessage[1])


def recv_file(file, serverSocket, queue):
    # Receive file content (should be first packet).
    message = queue.get()

    # TODO: Think about a better way to end the transfer.
    # TODO: Perhaps it could stop iterating if type IS NOT DATA.
    while message.type == DATA:
        logging.debug(
            f"Received file content from client {message.clientAddress}")

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
        logging.info(f"ERROR: Received a {message.type} packet at the end"
                     "of file upload")
        # TODO: Check if sending FIN is the best choice to close the client.
        serverSocket.sendto(FIN.encode(), message.clientAddress)


def send_file(file, serverSocket, clientAddress, queue):
    # Read first BUFSIZE bytes of the file
    data = file.read(BUFSIZE)

    while data:
        logging.debug("Read data from file")
        # Send bytes to the client
        serverSocket.sendto(data, clientAddress)
        logging.debug(f"Sent data to client {clientAddress}")

        # Receive answer from the client
        message = queue.get()

        logging.debug(
            f"Received message {message.type} from client {clientAddress}")

        # Check that is ACK
        if message.type != ACK:
            logging.error(f"ACK not received from client {clientAddress}")
            break  # TODO: wouldn't it be a return instead of a break?

        # Read another BUFSIZE bytes
        data = file.read(BUFSIZE)

    if message.type == FIN:
        logging.info(f"Received file from client {message.clientAddress}")
        serverSocket.sendto(FIN_ACK.encode(), message.clientAddress)
    elif not data:
        # Inform the client that the download is finished
        serverSocket.sendto(FIN.encode(), clientAddress)
        logging.debug(f"Sent {FIN} to client {clientAddress}")
        logging.info(f"Sent file to client {clientAddress}")
    else:
        logging.info(f"ERROR: Received a {message.type} packet at the end"
                     "of file upload")
        # TODO: Check if sending FIN is the best choice to close the client.
        serverSocket.sendto(FIN.encode(), message.clientAddress)


def handle_upload_request(clientAddress,
                          serverSocket,
                          queue,
                          dirpath,
                          filename):
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


def handle_download_request(clientAddress,
                            serverSocket,
                            queue,
                            dirpath,
                            filename):
    logging.info("Handling download request")

    if not os.path.exists(dirpath + filename):
        logging.error(f"File does not exist: {dirpath}/{filename}")
        # Send filename does not exist NAK.
        serverSocket.sendto(f'{NAK} File does not exist.'.encode(),
                            clientAddress)
        logging.debug(
            f"Sending {NAK} File does not exist to client {clientAddress}")
        return

    # Send filename received ACK.
    serverSocket.sendto(f'{ACK} Filename received.'.encode(), clientAddress)
    logging.debug(
        f"{ACK} Filename received sent to client {clientAddress}")

    file = open(dirpath + filename, 'rb')
    logging.debug(f"File to read from is {dirpath}/{filename}")

    send_file(file, serverSocket, clientAddress, queue)

    file.close()


def handle_action(address, socket, queue, dirpath):
    # TODO: Handle case where command is not upload and download.
    action = queue.get()
    if action.type == UPLOAD:
        handle_upload_request(address, socket, queue, dirpath, action.data)
    elif action.type == DOWNLOAD:
        handle_download_request(address, socket, queue, dirpath, action.data)
    else:
        logging.error(
            f"Received an invalid command from client {address}")


def is_ack(message):
    """
    Splits message into [ACK | NAK] + data
    """
    splited_message = message.decode().split(" ", 1)
    status = splited_message[0]

    response = ''
    if len(splited_message) == 2:
        response = splited_message[1]

    if status == ACK:
        return (True, response)
    elif status == NAK:
        return (False, response)
    else:
        return (False, "Unknown acknowledge: " + message.decode())


def send_filename(clientSocket, action, serverIP, port, filename):
    clientSocket.sendto((action + ' ' + filename).encode(),
                        (serverIP, port))
    logging.debug("Command and filename sent to server")
    message, _ = clientSocket.recvfrom(BUFSIZE)

    (ack, response) = is_ack(message)

    if not ack:
        raise NameError(response)
    logging.debug(f"{ACK} for first message received from server")
