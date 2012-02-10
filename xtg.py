#!/usr/bin/python
#
#------------------------------------------------------------------------------
# xtg V0.4.1 ( xml tools gui )
#------------------------------------------------------------------------------

import sys
import os
import subprocess
import commands
import string
import re
import urllib

from Tkinter import *
import tkMessageBox
import tkFileDialog

if( TkVersion < 8.5 ):
    sys.exit( "Fatal error: need Tkinter version 8.5 or higher." )

#------------------------------------------------------------------------------
# execute command, reuturn a tuple containing commands' output, stderr and return code
#------------------------------------------------------------------------------
# http://stackoverflow.com/questions/337863/python-popen-and-select-waiting-for-a-process-to-terminate-or-a-timeout 
def runcmd(cmd, timeout=None):
    ph_out = None # process output
    ph_err = None # stderr
    ph_ret = None # return code

    if sys.platform == 'win32':
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    elif sys.platform == 'linux2':
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True )

    # if timeout is not set wait for process to complete
    if not timeout:
        ph_ret = p.wait()
    else:
        fin_time = time.time() + timeout
        while p.poll() == None and fin_time > time.time():
            time.sleep(1)

        # if timeout reached, raise an exception
        if fin_time < time.time():
            os.kill(p.pid, signal.SIGKILL)
            raise OSError("Process timeout has been reached")
        ph_ret = p.returncode

    ph_out, ph_err = p.communicate()
    return (ph_out, ph_err, ph_ret)

#------------------------------------------------------------------------------
# checks whether `fpath` is an executable
#------------------------------------------------------------------------------
def is_exe( fpath ):
    return os.path.exists( fpath ) and os.access( fpath, os.X_OK )

#------------------------------------------------------------------------------
# which - will look for 'program' in folders in the %PATH% env. variable
#------------------------------------------------------------------------------
def which( program ):
    fpath, fname = os.path.split( program )
    if fpath:
        if is_exe( program ):
            return program
    else:
        for path in os.environ["PATH"].split( os.pathsep ):
            exe_file = os.path.join( path, program )
            if is_exe( exe_file ):
                return exe_file
    return None

#------------------------------------------------------------------------------
class App( Frame ):

    xml_file_path = ""
    xsd_file_path = ""

    # { <hash> : [ <well-formedness>, { <schema> : <validity> ... }] }
    # we know the XSD downloaded from the W3C website is well-formed and valid
    w3c_schema_hash = "c636445710b40614427479bd68bc812d389762ec"
    checked_files = { w3c_schema_hash : [ 1, { w3c_schema_hash : 1 } ] }

    def __init__( self, master = None ):
        Frame.__init__( self, master )

        self.last_folder=""
        self.xmlstar_bin=""
        self.xml_file_path = StringVar()
        self.xsd_file_path = StringVar()

        # this file will be used to validate the schema
        self.path_xsd_xsd = sys.path[0] + "/XMLSchema.xsd"

        self.grid()
        self.grid( padx=10, pady=10, sticky=N+S+E+W )
        self.create_widgets()
        self.check_xml_tool()

    def hashfile( self, filepath ):
        sha1 = hashlib.sha1()
        f = open( filepath, 'rb' )
        try:
            sha1.update( f.read() )
        finally:
            f.close()
        return sha1.hexdigest()

    # sets properties of `widget` to look nice as a status label
    #--------------------------------------------------------------------------
    def mk_status_label( self, widget ):
        widget[ "relief" ] = "ridge"
        widget[ "font" ] = "impact 12"
        widget[ "fg" ] = "gray"

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

        self.path_xml = Entry( self, text="XML file", textvariable=self.xml_file_path )
        self.path_xml.grid  ( row=0, column=1, sticky=E+W )

        self.browse_xml = Button( self, text="...", command=self.browse_for_xml )
        self.browse_xml.grid( row=0, column=2, padx=10, sticky=N+S+E+W)

        self.xml_wf = Label ( self, text="WELL-FORMEDNESS" )
        self.xml_wf.grid ( row=0, column=3, sticky=N+S+E+W, ipadx=10 )
        self.mk_status_label( self.xml_wf )

        self.xml_valid = Label ( self, text="VALIDITY" )
        self.xml_valid.grid ( row=0, column=4, sticky=N+S+E+W, ipadx=30 )
        self.mk_status_label( self.xml_valid )

        # XSD
        #-------------------------------------------------------------------
        self.label_xsd = Label( self, text="XSD file:" )
        self.label_xsd.grid ( row=1, column=0, sticky=N+S+E+W )

        self.path_xsd = Entry( self,text="XSD file", textvariable=self.xsd_file_path )
        self.path_xsd.grid  ( row=1, column=1, sticky=E+W )

        self.browse_xsd = Button( self, text="...", command=self.browse_for_schema )
        self.browse_xsd.grid( row=1, column=2, padx=10, sticky=N+S+E+W)

        self.xsd_wf = Label ( self, text="WELL-FORMEDNESS" )
        self.xsd_wf.grid ( row=1, column=3, sticky=N+S+E+W, ipadx=10 )
        self.mk_status_label( self.xsd_wf )

        self.xsd_valid = Label ( self, text="VALIDITY" )
        self.xsd_valid.grid ( row=1, column=4, sticky=N+S+E+W, ipadx=30 )
        self.mk_status_label( self.xsd_valid )

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
        self.errors[ "state" ] = DISABLED

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

    def process_xmlstar_val_err( self, err ):
        # regex which will detect the filenames of the loaded files

        xml_f = self.xml_file_path.get()
        xsd_f = self.xsd_file_path.get()
#        print "quoted xsd: " + urllib.quote( xsd_f, "/:" )

        re_str = "((?:" + re.escape( xml_f ) + \
                ")|(?:" + re.escape( xsd_f ) + \
                ")|(?:" + re.escape( "file:///" + urllib.quote( xml_f, "/:" ) ) + \
                ")|(?:" + re.escape( "file:///" + urllib.quote( xsd_f, "/:" ) ) + \
                "))\:(\d+)(:\.(\d+))?\:\s" 
        cre_filename  = re.compile( re_str )

        m = cre_filename.search( err )
        if not m:
            self.errors.insert( END, err.replace( "\r", "" ))
            return
        #
        self.errors.tag_configure('ill_element_name', foreground='#FA8072',    relief='raised')
        self.errors.tag_configure('ill_namespace',    foreground='grey',       relief='raised')
        self.errors.tag_configure('namespace',        foreground='grey',       relief='raised')
        self.errors.tag_configure('element_name',     foreground='#8FBC8F',    relief='raised')
        self.errors.tag_configure('dashes',           foreground='#708090',    relief='raised')

        # find all the occurences of the filename inside the string returned by xmlstar
        filename_iter = cre_filename.finditer( err )

        for match in filename_iter:
#            print "file: " + match.group(1) + "\n"
            self.errors.insert( END, "File:    " + os.path.basename( match.group(1) ) + "\n" )
            self.errors.insert( END, "Line:    " + match.group(2) + "\n" )
            if match.group(3):
                self.errors.insert( END, "Column:  " + match.group(3) + "\n" )
            message = err[ match.end():].replace( "\r", "" )

            self.errors.insert( END, "-----------------------------------------------------------------------" + "\n", ( "dashes" ) )
#            print "message: \n" + message

            if( message.find( "This element is not expected. Expected is one of" ) != -1 ):
                # regex for expected elements
                re_elements = "'?(" + re.escape( "{http://www.w3.org/2001/XMLSchema}" ) + ")([a-zA-z]+)['\s,]"
                cre_elements = re.compile( re_elements )


                printed_ill_element = False
                frags = cre_elements.split( message )
                i=0
                while ( i < len( frags ) - 1 ):
                    frag = frags[i]
                    if( frag == "Element " ):
                        self.errors.insert( END, frag, ( "error_msg_body" ) )
                        i = i+1
                        continue
                    if( frag == ": This element is not expected. Expected is one of ( " ):
                        self.errors.insert( END, frag + "\n", ( "error_msg_body" ) )
                        exp_ns = True
                        i = i+1
                        continue
                    if( frag ==" " ):
                        i = i+1
                        continue
                    if( frag ==")." ):
                        break
                    i = i+1
                    if( printed_ill_element ):
                        self.errors.insert( END, frag, ( "namespace" ) )
                        self.errors.insert( END, frags[i] + "\n", ( "element_name" ) )
                    else:
                        self.errors.insert( END, frag, ( "namespace" ) )
                        self.errors.insert( END, frags[i] + "\n", ( "ill_element_name" ) )
                        printed_ill_element = True
                    i = i+1
            else:
                self.errors.insert( END, message )

            self.errors.insert( END, "-----------------------------------------------------------------------" + "\n", ( "dashes" ) )

        self.errors[ "state" ] = DISABLED

    def run_xml_tool_command( self, command ):
        ( out, err, retcode ) = runcmd( command )
#        print "out: \n" + out
#        print "err: \n" + err
        if( retcode != 0 ):
            self.errors[ "state" ] = NORMAL
            self.errors.delete( 1.0, END )
            
#            re_xsd_str = "(" + re.escape( os.path.basename(self.xsd_file_path.get()) ) + ")"
            re_xsd_str = re.escape( os.path.basename(self.xsd_file_path.get()) )
#            print re_xsd_str
            cre_xsd    = re.compile( re_xsd_str )
            
            m = cre_xsd.search( err )
#            print m
            if( m ):
#                self.errors.insert( END, err )
                retcode = -100
#            else:
#                self.errors.insert( END, err )

        self.process_xmlstar_val_err( err )
        return retcode

    def reset_colors( self ):
        self.xml_wf     [ "fg" ] = "gray"
        self.xml_wf     [ "bg" ] = "lightgray"
        self.xml_valid  [ "fg" ] = "gray"
        self.xml_valid  [ "bg" ] = "lightgray"
        self.xsd_wf     [ "fg" ] = "gray"
        self.xsd_wf     [ "bg" ] = "lightgray"
        self.xsd_valid  [ "fg" ] = "gray"
        self.xsd_valid  [ "bg" ] = "lightgray"

    def update_colors( self, widget, code ):
        if( code == 0 ):
            widget[ "fg" ] = "white"
            widget[ "bg" ] = "green"
        else:
            widget[ "fg" ] = "white"
            widget[ "bg" ] = "red"

    def check_validity( self, xml_file, schema ):
        xml_hash = hashfile( xml_file )
        schema_hash = hashfile( schema )

        if( checked_files.has_key( xml_hash ) ):
            if( checked_files[ file_hash ][1].has_key( schema_hash ) ):
                return checked_files[ file_hash ][1][ schema_hash ]
            else:
                check_well_formedness( xml_file )
                pass

        schema_has = hashfile( schema )

    def check_well_formedness( self, xml_file ):
        file_hash = hashfile( xml_file )

        if checked_files.has_key( file_hash ):
            return checked_files[ file_hash ][0]
        else:
            cmd = self.xmlstar_bin + ' val --err --well-formed ' + xml_file
            retcode = run_xml_tool_command( cmd )
            checked_files[ file_hash ] = [ retcode, {} ]
            return retcode

    def check( self ):
        if( len( self.path_xml.get().strip()) == 0 ):
            tkMessageBox.showinfo( "Text", "You must select an XML file first" )
            return

        self.reset_colors()
        self.errors[ "state" ] = NORMAL
        self.errors.delete( 1.0, END )
        self.errors[ "state" ] = DISABLED

        # check XML well-formedness
        #-----------------------------------------------------------------------
        command = '"' + self.xmlstar_bin + '" val --err --well-formed "' + self.path_xml.get() + '"'
        retcode = self.run_xml_tool_command( command )

        self.update_colors( self.xml_wf, retcode )
        if( retcode != 0 ): return

        # check XSD well-formedness
        #-----------------------------------------------------------------------
        if( len( self.path_xsd.get().strip()) > 0 ):
            command = '"' + self.xmlstar_bin + '" val --err --well-formed "' + self.path_xsd.get() + '"'
            retcode = self.run_xml_tool_command( command )

            self.update_colors( self.xsd_wf, retcode )
            if( retcode != 0 ): return

            # check XSD validity
            #-----------------------------------------------------------------------
#            command = self.xmlstar_bin + ' val --err --xsd "' + self.path_xsd_xsd + '"' + ' "' + self.path_xsd.get() + '"'

#            retcode = self.run_xml_tool_command( command )

#            self.update_colors( self.xsd_valid, retcode )
#            if( retcode != 0 ): return

            # check XML validity
            #-----------------------------------------------------------------------
            command = '"' + self.xmlstar_bin + '" val --err --xsd "' + self.path_xsd.get() + '"' + ' "' + self.path_xml.get() + '"'

            retcode = self.run_xml_tool_command( command )
            if( retcode == -100 ):
                self.update_colors( self.xsd_valid, 1 )
                return
            if( retcode != 0):
                self.update_colors( self.xml_valid, retcode )
                self.update_colors( self.xsd_valid, 0 )
                return
            self.update_colors( self.xml_valid, 0 )
            self.update_colors( self.xsd_valid, 0 )

    def check_xml_tool( self ):
        if sys.platform == 'win32':
            xmlstar_bin_path = which( 'xml.exe' )
            if not xmlstar_bin_path or not is_exe( xmlstar_bin_path ):
                xmlstar_bin_path = sys.path[0] + '/xmlstarlet-1.3.1/xml.exe'  
                if not is_exe( xmlstar_bin_path ):
                    tkMessageBox.showinfo( "Text", "Cannot find the xmlstar executable" )
                    sys.exit()
        elif sys.platform == 'linux2':
            xmlstar_bin_path = which( 'xmlstarlet' )
            if not is_exe( xmlstar_bin_path ):
                tkMessageBox.showinfo( "Text", "Cannot find the xmlstar executable" )
                sys.exit()
        self.xmlstar_bin = xmlstar_bin_path
        print "bin: " + self.xmlstar_bin

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
app.master.title( "Xtg V0.4.1" )
app.mainloop()
