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

from Qt import QtWidgets, QtCore
from Qt import _loadUi

import listener
import util


PORT = 5051
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
MODULE_NAME = os.path.basename(MODULE_PATH)
UI_PATH = os.path.join(MODULE_PATH, 'ui', 'connector.ui')


class MayaConnector(QtWidgets.QMainWindow, listener.Connector):
    """
    Maya Connector Main Interface
    """

    def __init__(self, parent=None):
        """
        Initialization
        """
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        _loadUi(UI_PATH, self)

        listener.Connector.__init__(self)

        self.ui_connect_btn.clicked.connect(self.handle_connect)
        self.ui_disconnect_btn.clicked.connect(self.handle_disconnect)
        self.ui_run_all_btn.clicked.connect(self.execute)

    def closeEvent(self, event):
        """
        Override: perform clean-up: remove callback, close server, end thread
        """
        listener.Connector.cleanup(self)
        QtWidgets.QMainWindow.closeEvent(self, event)

    def execute(self):
        """
        Send command in script area for maya to execute
        """
        command = self.ui_script_edit.toPlainText()
        command = str(command).encode("string-escape")
        util.send_command(command)

    def start_listen(self):
        """
        Start listening to Maya's streaming port and display the return message
        """
        print("Connector up and listening")
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(ADDR)
        while True:
            # close thread
            if not self.is_running:
                break

            data = server.recvfrom(1024)
            message = data[0]

            # don't send message to client as it will cause infinite loop
            # FIXME: the gui update currently will randomly crash
            self.ui_log_edit.insertPlainText(message)
            scroll = self.ui_log_edit.verticalScrollBar()
            scroll.setValue(scroll.maximum())

        server.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    global win
    win = MayaConnector()
    win.show()
    sys.exit(app.exec_())
