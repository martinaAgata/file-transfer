import zlib
import struct

from .definitions import BUFSIZE

# TODO: Do we need to use this? We can write that no package is corrupt in hypothesis
def checksumCalculator(data):
    checksum = zlib.crc32(data)
    return checksum


def createHeader(bit):
    return struct.pack("!I", bit)


def send(socket, bit, data, address):
    header = createHeader(bit)
    socket.sendto(header + data, address)

def recv(socket):
    message, address = socket.recvfrom(BUFSIZE + 4)
    header = message[:4]
    data = message[4:]
    bit = struct.unpack("!I", header)[0]
    return bit, data, address
