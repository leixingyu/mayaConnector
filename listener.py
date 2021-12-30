"""
Module for setting up the listen server which sends command to
Maya's command port, and also actively listens to Maya's return message
from callback.

Requirement:
needs Maya to open a command port first, run it before connecting or
put it in the setup file for startup.

import maya.cmds as cmds
if not cmds.commandPort(":5050", query=True):
    cmds.commandPort(name=":5050")
"""


import os
import socket
import sys
import threading

from Qt import QtWidgets, QtCore
from Qt import _loadUi


PORT = 5051
COMMAND_PORT = 5050
SERVER = "127.0.0.1"

COMMAND_ADDR = (SERVER, COMMAND_PORT)
ADDR = (SERVER, PORT)

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(MODULE_PATH, 'logger.ui')


def send_command(command):
    """
    Send python command to opened maya command port

    :param command: str. full command in python
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(COMMAND_ADDR)
    # the command from external editor to maya
    command = 'python("{}")'.format(command)

    client.send(command)
    client.close()


def open_stream():
    """
    Send command to Maya to open output streaming
    """
    command = "import sys; " \
              "sys.path.append({}); " \
              "from {} import streamer; " \
              "streamer.open_stream()".format(MODULE_PATH, MODULE_PATH)
    send_command(command)


def close_stream():
    """
    Send command to Maya to close output streaming
    """
    command = "streamer.close_stream()"
    send_command(command)


class MayaLogger(QtWidgets.QMainWindow):
    """
    Maya Logger Main Interface
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(ADDR)

    listen_thread = None
    is_running = False

    def __init__(self, parent=None):
        """
        Initialization
        """
        super(MayaLogger, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        _loadUi(UI_PATH, self)

        self.ui_connect_btn.clicked.connect(self.handle_connect)
        self.ui_disconnect_btn.clicked.connect(self.handle_disconnect)
        self.ui_run_btn.clicked.connect(self.execute)

    def closeEvent(self, event):
        """
        Override: perform clean-up: remove callback, close server, end thread
        """
        self.handle_disconnect()
        self.server.close()
        super(MayaLogger, self).closeEvent(event)

    def execute(self):
        """
        Send command in script area for maya to execute
        """
        command = self.ui_script_edit.text()
        send_command(command)

    def handle_connect(self):
        """
        Open listen server on new thread to connect to Maya's streaming port
        """
        self.is_running = True
        self.listen_thread = threading.Thread(target=self.start_listen)
        self.listen_thread.start()
        open_stream()

    def handle_disconnect(self):
        """
        Close listen server thread connecting to Maya's streaming port
        """
        if self.is_running:
            self.is_running = False
            close_stream()
            print('Logger no longer listening')

    def start_listen(self):
        """
        Start listening to Maya's streaming port and display the return message
        """
        print("Logger up and listening")
        while True:
            if not self.is_running:
                break
            data = self.server.recvfrom(1024)
            message = data[0]
            # don't send message to client as it will cause infinite loop
            self.ui_log_edit.insertPlainText(message)
            scroll = self.ui_log_edit.verticalScrollBar()
            scroll.setValue(scroll.maximum())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    win = MayaLogger()
    win.show()
    sys.exit(app.exec_())
