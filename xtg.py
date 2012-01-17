# !/bin/env/python
#
#------------------------------------------------------------------------------
# xtg v0.1 ( xml tools gui )
# started 17 Jan 2012, 14:30
#------------------------------------------------------------------------------

import sys
from Tkinter import *

if( TkVersion < 8.5 ):
    sys.exit( "Fatal error: need Tkinter version 8.5 or higher." )

root = Tk()
root.title( "Xtg v0.1" )
root.mainloop()
