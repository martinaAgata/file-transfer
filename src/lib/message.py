from .definitions import ACTIONS, DATA


def retrieveMessageAttributes(message):
    """
    Returns a tuple with type and data retrieved from the message
    """
    decodedMessage = None

    try:
        decodedMessage = message.decode()
    except UnicodeDecodeError:
        return DATA, message

    splittedMessage = decodedMessage.split(" ", 1)

    if splittedMessage[0] in ACTIONS:
        if len(splittedMessage) == 1:
            return splittedMessage[0], ""
        return splittedMessage[0], splittedMessage[1]
    # Message is text
    return DATA, message


class Message:
    """
    Document me please!
    """

    def __init__(self, encodedMessage, clientAddress, bit):
        """
        Document me please!
        """
        self.type, self.data = retrieveMessageAttributes(encodedMessage)
        self.clientAddress = clientAddress
        self.bit = bit
