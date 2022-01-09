"""
Module to setup callback for streaming from Maya's (the client) side
"""


import errno
import socket
from cStringIO import StringIO

import maya.OpenMaya as om


SERVER = "127.0.0.1"
PORT = 5051


if 'STREAM_CALLBACK' in globals():
    try:
        om.MMessage.removeCallback(STREAM_CALLBACK)
    except RuntimeError:
        pass


STREAM_CALLBACK = None
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def open_stream(addr=(SERVER, PORT)):
    """
    Add callback to stream output of script editor when changed

    :param addr: tuple. ip address and port number
    """
    global STREAM_CALLBACK
    print("Streaming ScriptEditor at ({}:{})\n".format(addr[0], addr[1]))
    STREAM_CALLBACK = om.MCommandMessage.addCommandOutputCallback(
        stream_to_console,
        addr
    )


def close_stream():
    """
    Remove callback to stream output of script editor
    """
    global STREAM_CALLBACK
    print("Disable Streaming ScriptEditor\n")
    om.MMessage.removeCallback(STREAM_CALLBACK)
    STREAM_CALLBACK = None


def stream_to_console(msg, mtype, addr):
    """
    Stream result of the callback back to the listen server
    https://github.com/justinfx/MayaSublime/

    :param msg: str. MEL command being executed (i.e. callback output)
    :param mtype: OpenMaya.MMessage.MessageType. type of the message
    :param addr: tuple. ip address and port number
    """
    buf = StringIO()
    buf.seek(0)
    buf.truncate()

    if mtype == om.MCommandMessage.kWarning:
        buf.write('# Warning: ')
        buf.write(msg)
        buf.write(' #\n')

    elif mtype == om.MCommandMessage.kError:
        buf.write('// Error: ')
        buf.write(msg)
        buf.write(' //\n')

    elif mtype == om.MCommandMessage.kResult:
        buf.write('# Result: ')
        buf.write(msg)
        buf.write(' #\n')
    else:
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
