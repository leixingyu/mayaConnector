import socket
import threading

import util


PORT = 5051
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)


class Connector(object):

    def __init__(self):
        """
        Initialization
        """
        self.is_running = False

    def cleanup(self):
        """
        Perform clean-up operation
        """
        self.handle_disconnect()

    def handle_connect(self):
        """
        Open listen server on new thread to connect to client's streaming port
        """
        self.is_running = True
        listen_thread = threading.Thread(target=self.start_listen)
        listen_thread.start()
        util.open_stream()

    def handle_disconnect(self):
        """
        Close listen server thread connecting to client's streaming port
        """
        if self.is_running:
            self.is_running = False
            util.close_stream()
            print('Connector no longer listening')

    def start_listen(self):
        """
        Start listening to client streaming port and display the return message
        """
        print("Connector up and listening")
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(ADDR)
        while True:
            if not self.is_running:
                # close thread
                break

            data = server.recvfrom(1024)
            message = data[0]
            print(message)

        server.close()
