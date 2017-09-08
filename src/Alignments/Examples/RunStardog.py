import Alignments.Utility as Ut
import os
import Alignments.Settings as St
import Alignments.Server_Settings as Srv


import subprocess
# https://docupub.com/pdfmerge/

print "RUNNING THE STARDOG SERVER"
bat_path = "C:/stardogStart.bat"

lock_file = [name for name in os.listdir(Srv.settings[St.stardog_data_path]) if name.endswith('.lock')]
if len(lock_file) > 0:
    print "THE SERVER WAS IS ALREADY ON."
else:
    subprocess.check_call(bat_path, shell=True)

# os.chmod(bat_path, stat.S_IRWXO)
#
# Ut.batch_load("C:/stardogStart.bat")
print "Done"