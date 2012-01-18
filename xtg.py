# !/bin/env/python
#
#------------------------------------------------------------------------------
# xtg v0.1 ( xml tools gui )
# started 17 Jan 2012, 14:30
#------------------------------------------------------------------------------

import sys
import os
from subprocess import call

from Tkinter import *
import tkMessageBox
import tkFileDialog

if( TkVersion < 8.5 ):
    sys.exit( "Fatal error: need Tkinter version 8.5 or higher." )

#------------------------------------------------------------------------------
class App( Frame ):

    def __init__( self, master = None ):
        Frame.__init__( self, master )

        self.grid()
        self.grid( padx=10, pady=10, sticky=N+S+E+W )
        self.create_widgets()
        self.check_xml_tool()

        self.last_folder=""
        self.xmlstar_bin=""

        self.check_xml_tool()

    def create_widgets( self ):
        top = self.winfo_toplevel()
        top.rowconfigure( 0, weight=1 )
        top.columnconfigure ( 0, weight=0 )
        self.columnconfigure( 0, weight=0 )
        self.columnconfigure( 1, weight=1 )
        self.columnconfigure( 2, weight=0 )

        # XML
        #-------------------------------------------------------------------
        self.label_xml = Label( self, text="XML file:" )
        self.label_xml.grid ( row=0, column=0, sticky=N+S+E+W )

        self.path_xml = Entry( self,text="XML file" )
        self.path_xml.grid  ( row=0, column=1, sticky=E+W )

        self.browse_xml = Button( self, text="...", command=self.browse_for_xml )
        self.browse_xml.grid( row=0, column=2, padx=10, sticky=N+S+E+W)

        self.xml_wf = Label ( self, text="WELL-FORMEDNESS" )
        self.xml_wf.grid ( row=0, column=3, sticky=N+S+E+W, ipadx=10 )
        self.xml_wf[ "relief" ] = "ridge"
        self.xml_wf[ "font" ] = "impact 12"
        self.xml_wf[ "fg" ] = "gray"

        self.xml_valid = Label ( self, text="VALIDITY" )
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

        self.browse_xsd = Button( self, text="...", command=self.browse_for_schema )
        self.browse_xsd.grid( row=1, column=2, padx=10, sticky=N+S+E+W)

        self.xsd_wf = Label ( self, text="WELL-FORMEDNESS" )
        self.xsd_wf.grid ( row=1, column=3, sticky=N+S+E+W, ipadx=10 )
        self.xsd_wf[ "relief" ] = "ridge"
        self.xsd_wf[ "font" ] = "impact 12"
        self.xsd_wf[ "fg" ] = "gray"

        # Check
        #-------------------------------------------------------------------
        self.check_btn = Button(self, text="Check", command=self.check)
        self.check_btn.grid( row=2, column=0, columnspan=5, pady=10, padx=10, sticky=N+S+E+W)
        self.check_btn[ "font" ] = "impact 12"

        # Errors
        #-------------------------------------------------------------------
        self.errors = Text( self )
        self.errors.grid( row=3, column=0, columnspan=5, sticky=N+S+E+W )
        self.errors[ "fg" ] = "lightgray"
        self.errors[ "bg" ] = "black"

    def run_command( self, command ):
        print( "running command: \n" + command )
        try:
            retcode =  call( command )
            if retcode < 0:
                print >>sys.stderr, "Child was terminated by signal", -retcode
            elif retcode == 0:
                pass
            else:
                print >>sys.stderr, "Child returned", retcode
        except OSError, e:
            print >>sys.stderr, "Execution failed:", e
        except KeyboardInterrupt, e:
            print >>sys.stderr, "Keyboard interrupt", e
        except:
            print "Unexpected error:", sys.exc_info()[0]
        return retcode


    def check( self ):
        if( len( self.path_xml.get().strip()) == 0 ):
            tkMessageBox.showinfo( "Text", "You must select an XML file first" )
            return

        # check XML well-formedness
        #-----------------------------------------------------------------------
        self.xml_wf[ "fg" ] = "gray"
        self.xml_wf[ "bg" ] = "SystemButtonFace"

        command = self.xmlstar_bin + ' val --well-formed ' + self.path_xml.get()
        retcode = self.run_command( command )
        
        if( retcode == 0 ):
            self.xml_wf[ "fg" ] = "white"
            self.xml_wf[ "bg" ] = "green"
        else:
            self.xml_wf[ "fg" ] = "white"
            self.xml_wf[ "bg" ] = "red"

        # check XSD well-formedness
        #-----------------------------------------------------------------------
        if( len( self.path_xsd.get().strip()) > 0 ):
            self.xsd_wf[ "fg" ] = "gray"
            self.xsd_wf[ "bg" ] = "SystemButtonFace"

            command = self.xmlstar_bin + ' val --well-formed ' + self.path_xsd.get()
            retcode = self.run_command( command )
            
            if( retcode == 0 ):
                self.xsd_wf[ "fg" ] = "white"
                self.xsd_wf[ "bg" ] = "green"
            else:
                self.xsd_wf[ "fg" ] = "white"
                self.xsd_wf[ "bg" ] = "red"

    def check_xml_tool( self ):
        default_path = sys.path[0] + '/xmlstarlet-1.3.0/xml.exe'  
        if not os.path.isfile( default_path ):
            sys.exit( "Cannof find XML tool: xmlstarlet" )
        else:
            self.xmlstar_bin = default_path

    def browse_for_xml( self ):
        options = {}
        options[ "title" ]      = "Select XML File"
        options[ "filetypes" ]  = [ ("xml","*.xml"), ("All files","*") ]
        if( len( self.last_folder.strip()) > 0 ):
            options[ "initialdir" ] = self.last_folder

        xml_file = tkFileDialog.askopenfilename( **options )
        if( xml_file ):
            if( os.path.isfile( xml_file )):
                self.path_xml.delete( 0, len( self.path_xml.get()))
                self.path_xml.insert( 0, xml_file )
                self.last_folder = os.path.dirname( xml_file )

    def browse_for_schema( self ):
        options = {}
        options[ "title" ]      = "Select a schema"
        options[ "filetypes" ]  = [ ("XSD Schema","*.xsd"), ("RelaxNG Schema","*.rng"), ("All files","*") ]
        if( len( self.last_folder.strip()) > 0 ):
            options[ "initialdir" ] = self.last_folder

        xsd_file = tkFileDialog.askopenfilename( **options )
        if( xsd_file ):
            if( os.path.isfile( xsd_file )):
                self.path_xsd.delete( 0, len( self.path_xsd.get()))
                self.path_xsd.insert( 0, xsd_file )
                self.last_folder = os.path.dirname( xsd_file )

#------------------------------------------------------------------------------
app = App()
app.master.title( "Xtg v0.1" )
app.mainloop()
