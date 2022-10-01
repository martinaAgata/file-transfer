from .definitions import (ACK, NAK)


def process_first_message(encodedFirstMessage):
    firstMessage = encodedFirstMessage.decode().split()
    return (firstMessage[0], firstMessage[1])


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