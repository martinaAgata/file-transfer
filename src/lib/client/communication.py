import logging
from lib.definitions import BUFSIZE, ACK
from lib.utils import is_ack


def send_filename(clientSocket, action, serverIP, port, filename):
    clientSocket.sendto((action + ' ' + filename).encode(),
                        (serverIP, port))
    logging.debug("Command and filename sent to server")
    message, _ = clientSocket.recvfrom(BUFSIZE)

    (ack, response) = is_ack(message)

    if not ack:
        raise NameError(response)
    logging.debug(f"{ACK} for first message received from server")
