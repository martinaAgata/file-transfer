from ..definitions import ACTIONS, DATA


# TODO: check if should be moved to some utils file.
def retrieveMessageAttributes(message):
    """
    Returns a tuple with type and data retrieved from the message
    """
    decodedMessage = message.decode()
    splittedMessage = decodedMessage.split(" ", 1)
    if splittedMessage[0] in ACTIONS:  # TODO: move this.
        return splittedMessage[0], splittedMessage[1]
    else:
        return DATA, decodedMessage


class Message:
    """
    Document me please!
    """
    def __init__(self, encodedMessage, clientAddress):
        """
        Document me please!
        """
        self.type, self.data = retrieveMessageAttributes(encodedMessage)
        self.clientAddress = clientAddress
