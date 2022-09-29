from lib.definitions import ACK, NAK, FIN, DATA

# Splits message into [ACK | NAK] + data
def decode(message):
    splited_message = message.decode().split(" ", 1)
    status = splited_message[0]

    response = ''
    if len(splited_message) == 2:
        response = splited_message[1]

    if status == FIN:
        return status, ""

    if status not in [ACK, NAK, DATA]:
        return (None, "Unknown acknowledge: " + message.decode())
    
    return (status, response)
