import Alignments.Utility as Ut
import os
import Alignments.Settings as St
import Alignments.Server_Settings as Srv
# https://docupub.com/pdfmerge/

# directory = "C:\Program Files\stardog-4.1.3\data"
# Ut.listening(directory)


print "STOPPING THE STARDOG SERVER"

lock_file = [name for name in os.listdir(Srv.settings[St.stardog_data_path]) if name.endswith('.lock')]

if len(lock_file) > 0:
    off = Ut.batch_load("C:\stardogStop.bat")
    print "RESPONSE: {}".format(off["result"])
else:
    print "THE SERVER WAS NOT ON."