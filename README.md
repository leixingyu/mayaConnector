<div align="center">
<h1 align="center">Maya Connector</h1>

  <p align="center">
    An external tool capable of sending command to Maya and stream its output
    <br />
    <a href="https://youtu.be/kVdCGMWfJdE">Demo</a>
  </p>
</div>

## About The Project

<br>

<div align="center">
<img src="https://i.imgur.com/89SJibG.gif" alt="maya-connector" width="100%"/>
</div>

Although there are a lot of tools that can run internally in Maya which facilitate
the pipeline. The capability of communicating (monitor and control) with Maya externally is very handy.

I covered the development of this tool in more detailed here: 
[Part 1](https://www.xingyulei.com/post/maya-commandport/) |
[Part 2](https://www.xingyulei.com/post/maya-streaming/).

This tool has two major components:
1. command port: sending commands to maya to execute
2. output streaming: actively listening/receiving maya outputs

## Getting Started

1. Unzip the **maya-connector** package

2. Launch Maya and open port `5050`:
    ```python
    import maya.cmds as cmds
    port = 5050
    if not cmds.commandPort(":{}".format(port), query=True):
        cmds.commandPort(name=":{}".format(port))
    ```

3. Run `main.py` through `mayapy` or `python` externally
4. Click the **connect** button to establish streaming connection
5. Use the tool like an external script editor


## Features

- code editor with syntax highlighting and line counter
- save/open script
- execute selected script or all
- clear viewport

## Reference

[Google Group - Receiving data from commandPort](https://groups.google.com/g/python_inside_maya/c/7AgWlldtvbE/m/zUTQlAcjBgAJ?pli=1)

[Stack Overflow - c socket programming, only receiving one line at a time](https://stackoverflow.com/questions/10434525/c-socket-programming-only-receiving-one-line-at-a-time)

[CG Talk - Telnet or Socket: no result back from Maya](https://forums.cgsociety.org/t/telnet-or-socket-no-result-back-from-maya/1730817/2)

[Youtube - Python Socket Programming Tutorial](https://youtu.be/3QiPPX-KeSc)

[Maya Help - OpenMaya.MCommandMessage Class Reference](https://help.autodesk.com/view/MAYAUL/2016/ENU/?guid=__py_ref_class_open_maya_1_1_m_command_message_html)

[Google Groups - Extracting data from Output Window](https://groups.google.com/g/python_inside_maya/c/pp_E7rCs7d0)

[Github - MayaCharm](https://github.com/cmcpasserby/MayaCharm)

[Github - MayaSublime](https://github.com/justinfx/MayaSublime/)


