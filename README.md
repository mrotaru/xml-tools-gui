XML Tools GUI
-------------

Dependencies: 
    - Python 2.6+ with Tkinter 8.5+ 
    - the `xmlstar` toolkit; `xtg.py` must be in the same folder as `xmlstar`

A Python script which aims to provide a user-friendly graphical user interface
to command line utilities which work with XML stuff. At the moment, it supports
only the [ XMLStarlet ](http://xmlstar.sourceforge.net) toolkit.

The validity and well-formedness test are performed in the following order:
- is the XML well-formed ?
- is the XSD well-formed ?
- is the XSD valid ?
- is the XML valid ?
