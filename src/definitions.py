import logging

DEFAULT_SERVER_IP = '127.0.0.1'
DEFAULT_SERVER_PORT = 12000
BUFSIZE = 2048
DEFAULT_DIRPATH = 'files/' # TODO: perhaps a CURRENT_DIRPATH is needed
DEFAULT_LOGGING_LEVEL = logging.INFO
DEFAULT_DOWNLOAD_FILEPATH = '../../downloads/'
DEFAULT_UPLOAD_FILEPATH = '../../resources/'

UPLOAD = "upload"
DOWNLOAD = "download"
ACK = "ACK"
NAK = "NAK"
FIN = "FIN"
FIN_ACK = "FIN_ACK"
ACTIONS = set(UPLOAD, DOWNLOAD, ACK, NAK, FIN)
DATA = "DATA"