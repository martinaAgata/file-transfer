import zlib
import struct

BUFSIZE = 2048

# TODO: Do we need to use this? We can write that no package is corrupt in hypothesis
def checksumCalculator(data):
    checksum = zlib.crc32(data)
    return checksum


def createHeader(bit):
    return struct.pack("!I", bit)


def send(socket, bit, data, serverIP, port=None):
    header = createHeader(bit)
    if not port:
        socket.sendto(header + data, serverIP)
    else:
        socket.sendto(header + data, (serverIP, port))

def recv(socket):
    message, address = socket.recvfrom(BUFSIZE + 4)
    header = message[:4]
    data = message[4:]
    bit = struct.unpack("!I", header)[0]
    return bit, data, address
