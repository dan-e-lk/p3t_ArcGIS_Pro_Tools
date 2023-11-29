# output messages through arcpy, and store all the messages to create log file later.

import os, arcpy

class print_n_log():
    def __init__(self):
        self.all_msg = ''

    def print2(self, msg, msgtype = 'msg', do_not_log = False):

        print(msg)
        if msgtype == 'msg':
            arcpy.AddMessage(msg)
        elif msgtype == 'warning':
            arcpy.AddWarning(msg)
        elif msgtype == 'error':
            arcpy.AddError(msg)        

        # Add newline to the message string AFTER the message is sent to arcpy
        if not do_not_log:
            msg = msg + '\n'
            self.all_msg += msg


    def create_logfile(self, outpath, outfile):

        with open(os.path.join(outpath,outfile),"a") as f:
            f.writelines(self.all_msg)
