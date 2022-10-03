import logging


DEFAULT_SERVER_IP = '127.0.0.1'
DEFAULT_SERVER_PORT = 22000
BUFSIZE = 2048
DEFAULT_DIRPATH = 'files/'  # TODO: perhaps a CURRENT_DIRPATH is needed
DEFAULT_LOGGING_LEVEL = logging.INFO
DEFAULT_DOWNLOAD_FILEPATH = '../downloads/'  # TODO: create if does not exist
DEFAULT_UPLOAD_FILEPATH = 'lib/resources/'
TIMEOUT = 0.01
MAX_ALLOWED_TIMEOUTS = 5

UPLOAD = "upload"
DOWNLOAD = "download"
ACK = "ACK"
NAK = "NAK"
FIN = "FIN"
FIN_ACK = "FIN_ACK"
ACK_ACK = "ACK_ACK"
ACTIONS = {UPLOAD, DOWNLOAD, ACK, NAK, FIN, FIN_ACK}
DATA = "DATA"

GBN_BASE_PACKAGE_TIMEOUT = 0.1
GBN_RECEIVER_TIMEOUT = 15

SNW_BIT = 0
GBN_BIT = 1

DEFAULT_DOWNLOAD_PROTOCOL_BIT = GBN_BIT
DEFAULT_UPLOAD_PROTOCOL_BIT = SNW_BIT
