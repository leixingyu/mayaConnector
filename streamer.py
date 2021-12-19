import errno
import socket
from cStringIO import StringIO

import maya.OpenMaya as om


SERVER = '127.0.0.1'
PORT = 5051


if 'STREAM_CALLBACK' in globals():
    try:
        om.MMessage.removeCallback(STREAM_CALLBACK)
    except RuntimeError:
        pass


STREAM_CALLBACK = None
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def open_stream(addr=(SERVER, PORT)):
    global STREAM_CALLBACK
    print("Streaming ScriptEditor at ({}:{})\n".format(addr[0], addr[1]))
    STREAM_CALLBACK = om.MCommandMessage.addCommandOutputCallback(
        stream_to_console,
        addr
    )


def close_stream():
    global STREAM_CALLBACK
    print("Disable Streaming ScriptEditor\n")
    om.MMessage.removeCallback(STREAM_CALLBACK)
    STREAM_CALLBACK = None


def stream_to_console(msg, mtype, addr):
    buf = StringIO()
    buf.seek(0)
    buf.truncate()
    buf.write(msg)
    buf.seek(0)
    buf_size = 8*1024
    while True:
        while buf_size > 0:
            pos = buf.tell()

            part = buf.read(buf_size)
            if not part:
                return
            try:
                client.sendto(part, addr)
            except Exception as e:
                if e.errno == errno.EMSGSIZE:
                    buf_size /= 2
                    buf.seek(pos)
                    continue
                raise
            break
