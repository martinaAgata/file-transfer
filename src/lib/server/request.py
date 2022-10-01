import logging
from ..definitions import DOWNLOAD, UPLOAD
from .download.request import handle as handle_download_request
from .upload.request import handle as handle_upload_request


def handle_action(address, socket, queue, dirpath):
    # TODO: Handle case where command is not upload and download.
    action = queue.get()
    if action.type == UPLOAD:
        handle_upload_request(address, socket, queue, dirpath, action.data)
    elif action.type == DOWNLOAD:
        handle_download_request(address, socket, queue, dirpath, action.data)
    else:
        logging.error(f"Received an invalid command from client {address}")
