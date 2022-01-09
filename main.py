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

from Qt import QtWidgets, QtCore, QtGui
from Qt import _loadUi

import listener
import util
from codeEditor import codeEditor
from codeEditor.highlighter import pyHighlight


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
    message_received = QtCore.Signal(str)

    def __init__(self, parent=None):
        """
        Initialization
        """
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        _loadUi(UI_PATH, self)

        listener.Connector.__init__(self)

        self.ui_script_edit = codeEditor.CodeEditor()
        self.ui_python_layout.addWidget(self.ui_script_edit)
        highlight = pyHighlight.PythonHighlighter(self.ui_script_edit.document())

        self.ui_run_all_btn.setIcon(QtGui.QIcon(":/executeAll.png"))
        self.ui_run_sel_btn.setIcon(QtGui.QIcon(":/execute.png"))
        self.ui_connect_btn.setIcon(QtGui.QIcon(":/connect.png"))
        self.ui_disconnect_btn.setIcon(QtGui.QIcon(":/disconnect.png"))
        self.ui_clear_log_btn.setIcon(QtGui.QIcon(":/clearHistory.png"))
        self.ui_clear_script_btn.setIcon(QtGui.QIcon(":/clearInput.png"))
        self.ui_clear_both_btn.setIcon(QtGui.QIcon(":/clearAll.png"))

        self.ui_connect_btn.clicked.connect(self.handle_connect)
        self.ui_disconnect_btn.clicked.connect(self.handle_disconnect)
        self.ui_run_all_btn.clicked.connect(self.execute)
        self.ui_run_sel_btn.clicked.connect(self.execute_sel)
        self.ui_clear_log_btn.clicked.connect(self.clear_log)
        self.ui_clear_script_btn.clicked.connect(self.clear_script)
        self.ui_clear_both_btn.clicked.connect(self.clear_all)
        self.ui_save_action.triggered.connect(self.save_script)
        self.ui_open_action.triggered.connect(self.open_script)

        self.message_received.connect(self.update_logger)

    def closeEvent(self, event):
        """
        Override: perform clean-up: remove callback, close server, end thread
        """
        listener.Connector.cleanup(self)
        QtWidgets.QMainWindow.closeEvent(self, event)

    def execute(self):
        """
        Send all command in script area for maya to execute
        """
        command = self.ui_script_edit.toPlainText()
        command = str(command).encode("string-escape")
        util.send_command(command)

    def execute_sel(self):
        """
        Send selected command in script area for maya to execute
        """
        command = self.ui_script_edit.textCursor().selection().toPlainText()
        command = str(command).encode("string-escape")
        util.send_command(command)

    def start_listen(self):
        """
        Override: Listening to Maya's streaming port and emit update ui signal
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
            # use signal to sync result logging, this avoid crashes
            self.message_received.emit(message)

        server.close()

    def update_logger(self, message):
        """
        Update ui field with messages

        :param message: str. text to update the logger filed
        """
        self.ui_log_edit.insertPlainText(message)
        scroll = self.ui_log_edit.verticalScrollBar()
        scroll.setValue(scroll.maximum())

    def clear_script(self):
        """
        Clear script edit area
        """
        self.ui_script_edit.clear()

    def clear_log(self):
        """
        Clear history logging area
        """
        self.ui_log_edit.clear()

    def clear_all(self):
        """
        Clear both script edit area and history logging area
        """
        self.clear_log()
        self.clear_script()

    def open_script(self):
        """
        Open python file to script edit area
        """
        path = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Open Script",
            MODULE_PATH,
            filter="*.py")[0]

        if not path:
            return

        with open(path, 'r') as f:
            output = f.read()
            self.ui_script_edit.setPlainText(output)

    def save_script(self):
        """
        Save script edit area as a python file
        """
        path = QtWidgets.QFileDialog.getSaveFileName(
            None,
            "Save Script As...",
            MODULE_PATH,
            filter="*.py")[0]

        if not path:
            return

        command = self.ui_script_edit.toPlainText()
        with open(path, 'w') as f:
            f.write(command)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QResource.registerResource(
        os.path.join(MODULE_PATH, "icons", "icons.rcc"))

    global win
    win = MayaConnector()
    win.show()
    sys.exit(app.exec_())
