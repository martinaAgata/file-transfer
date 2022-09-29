import logging
from lib.client import decode, encode
from lib.definitions import BUFSIZE, ACK


def send_filename(type, filename, server, clientSocket):
    clientSocket.sendto(encode(type, filename), server)
    logging.debug("Command and filename sent to server")
    message, _ = clientSocket.recvfrom(BUFSIZE)

    (type, response) = decode(message)

    if type != ACK:
        raise NameError(response)

    logging.debug("ACK for first message received from server")
