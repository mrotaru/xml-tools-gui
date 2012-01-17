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

#------------------------------------------------------------------------------
class App( Frame ):

    def __init__( self, master = None ):
        Frame.__init__( self, master )
#        master.geometry="300x300+40+10"

        self.grid()
        self.grid( padx=10, pady=10, sticky=N+S+E+W )
        self.create_widgets()

    def create_widgets( self ):
        top = self.winfo_toplevel()
        top.rowconfigure( 0, weight=1 )
        top.columnconfigure( 0, weight=0 )
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # XML
        #-------------------------------------------------------------------
        self.label_xml = Label( self, text="XML file:" )
        self.label_xml.grid ( row=0, column=0, sticky=N+S+E+W )

        self.path_xml = Entry( self,text="XML file" )
        self.path_xml.grid  ( row=0, column=1, sticky=E+W )

        self.browse_xml = Button(self, text="...", command=self.quit)
        self.browse_xml.grid( row=0, column=2, padx=10, sticky=N+S+E+W)

        self.xml_wf = Label ( self, text="WELL-FORMED" )
        self.xml_wf.grid ( row=0, column=3, sticky=N+S+E+W, ipadx=10 )
        self.xml_wf[ "relief" ] = "ridge"
        self.xml_wf[ "font" ] = "impact 12"
        self.xml_wf[ "fg" ] = "gray"

        self.xml_valid = Label ( self, text="VALID" )
        self.xml_valid.grid ( row=0, column=4, sticky=N+S+E+W, ipadx=10 )
        self.xml_valid[ "relief" ] = "ridge"
        self.xml_valid[ "font" ] = "impact 12"
        self.xml_valid[ "fg" ] = "gray"

        # XSD
        #-------------------------------------------------------------------
        self.label_xsd = Label( self, text="XSD file:" )
        self.label_xsd.grid ( row=1, column=0, sticky=N+S+E+W )

        self.path_xsd = Entry( self,text="XSD file" )
        self.path_xsd.grid  ( row=1, column=1, sticky=E+W )

        self.browse_xsd = Button(self, text="...", command=self.quit)
        self.browse_xsd.grid( row=1, column=2, padx=10, sticky=N+S+E+W)

        self.xsd_wf = Label ( self, text="WELL-FORMED" )
        self.xsd_wf.grid ( row=1, column=3, sticky=N+S+E+W, ipadx=10 )
        self.xsd_wf[ "relief" ] = "ridge"
        self.xsd_wf[ "font" ] = "impact 12"
        self.xsd_wf[ "fg" ] = "gray"

        # Check
        #-------------------------------------------------------------------
        self.check = Button(self, text="Check", command=self.quit)
        self.check.grid( row=2, column=0, columnspan=5, pady=10, padx=10, sticky=N+S+E+W)
        self.check[ "font" ] = "impact 12"

        # Errors
        #-------------------------------------------------------------------
        self.errors = Text( self )
        self.errors.grid( row=3, column=0, columnspan=5, sticky=N+S+E+W )
        self.errors[ "fg" ] = "lightgray"
        self.errors[ "bg" ] = "black"

    def display( self ):
        TkMessageBox.showinfo("Text", "You typed: %s" % self.enText.get())    

#------------------------------------------------------------------------------
app = App()
app.master.title( "Xtg v0.1" )
app.mainloop()
