from app import app
import os
import requests
import Alignments.Settings as St
import Alignments.Utility as Ut
import Alignments.Server_Settings as Svr

# https://docupub.com/pdfmerge/
print "\nRUNNING THE LENTICULAR LENS SERVER"
if __name__ == "__main__":

    lock_file = [name for name in os.listdir(Svr.settings[St.stardog_data_path]) if name.endswith('.lock')]
    try:
        response = requests.get("http://{}".format(Svr.settings[St.stardog_host_name]))
    except Exception as err:
        response = str(err)

    if len(lock_file) > 0  and str(response).__contains__("200"):
        "NOTHING TO DO AS THE SERVER WAS IS STILL ON."
        # bat_path = "{}stardogStop{}".format(Svr.SRC_DIR, Ut.batch_extension())
        # Ut.stardog_off(bat_path)
    else:
        "SWITCHING ON THE SERVER..."
        bat_path = "{}stardogStart{}".format(Svr.SRC_DIR, Ut.batch_extension())
        Ut.stardog_on(bat_path)

    app.run(host="0.0.0.0", port=5077)
