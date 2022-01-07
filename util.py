import os
import socket


COMMAND_PORT = 5050
SERVER = "127.0.0.1"
COMMAND_ADDR = (SERVER, COMMAND_PORT)

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
MODULE_NAME = os.path.basename(MODULE_PATH)


def send_command(command):
    """
    Send python command to opened maya command port

    :param command: str. full command in python
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(COMMAND_ADDR)
    # this resolves the mixed quotation conflicts
    command = 'python("' + command.replace(r'"', r'\"') + '")'

    client.send(command)
    client.close()


def open_stream():
    """
    Send command to Maya to open output streaming
    """
    command = r"import sys; " \
              r"sys.path.append('{}'); " \
              r"from {} import streamer; " \
              r"streamer.open_stream()".format(MODULE_PATH, MODULE_NAME)
    send_command(command)


def close_stream():
    """
    Send command to Maya to close output streaming
    """
    command = "streamer.close_stream()"
    send_command(command)
