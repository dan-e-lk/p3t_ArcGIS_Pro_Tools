#-------------------------------------------------------------------------------
# Name:         Messages
# Purpose:      Create a common message for interpreter results and for the Arc Toolbox message window.
#
# Authors:      kimda and littleto
#
# Created:     01-02-2018
# Copyright:   (c) littleto 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
r"""
This module is for creating messages for the interpreter and for the Arc Toolbox message window.

msg, is the message to be used.
msgtype, is the level of the message to generate from arcpy: message or warning. It affects the colour of the message in the
Arc Toolbox script runtime window. The default is message.

This module required 'import arcpy'
"""

import os, arcpy

def print2(msg, msgtype = 'msg'):
    r""" print, arcmap AddMessage and return string all in one!

    msg = arcpy.AddMessage
    warning = arcpy.AddWarning

    A newline is added to the message string AFTER the message is sent to
    arcpy; the return includes a newline.
    """

    print(msg)
    if msgtype == 'msg':
        arcpy.AddMessage(msg)
    elif msgtype == 'warning':
        arcpy.AddWarning(msg)
    elif msgtype == 'error':
        arcpy.AddError(msg)        

    # Add newline to the message string AFTER the message is sent to arcpy; the
    # return includes a newline.
    msg = str(msg) + '\n'

    return msg

def output(outpath, outfile, msg):
    r""" Write the messages to an output path.

    outpath = the path upon which the file outfile file will be created.
    outfile = the file name for the output file.

        e.g.,   outpath = r"C:\Users\littleto\data\ner_sfu_revision_project\project_data\NER pforest only dataset"
                outfile = 'compile_canopies_log_%(end)s.txt' %{'end':endtime.strftime('%Y_%m_%d_%H%M')}
                    NOTE:   the outfile in the example above required that datetime be imported in the module that
                            calls this function.
                msg = The message to added to the outfile, as a string.

    The 'with' statement is supposed to improve performance.
    """

    with open(os.path.join(outpath,outfile),"a") as f:
        f.writelines(msg)
