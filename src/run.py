from app import app
import os
import requests
import Alignments.Settings as St
import Alignments.Utility as Ut
import Alignments.Query as Qry
import Alignments.Server_Settings as Svr

# https://docupub.com/pdfmerge/
print "\nRUNNING THE LENTICULAR LENS SERVER"
if __name__ == "__main__":

    lock_file = [name for name in os.listdir(Svr.settings[St.stardog_data_path]) if name.endswith('.lock')]
    # print lock_file

    try:
        response = requests.get("http://{}".format(Svr.settings[St.stardog_host_name]))
        # response = Qry.endpoint("SELECT * {?sub ?obj ?pred} LIMIT 1")

    except Exception as err:
        response = str(err)

    # print response
    if str(response).__contains__("401"):
        print "THE STARDOG SERVER IS ON AND REQUIRES PASSWORD."

    if len(lock_file) > 0 and (
                str(response).__contains__("200") or
                str(response).__contains__("401") or
                str(response).__contains__("No connection") is False):
        "NOTHING TO DO AS THE SERVER IS STILL ON."

    else:
        print "\n>>> ", response
        "SWITCHING ON THE SERVER..."
        bat_path = "{}stardogStart{}".format(Svr.SRC_DIR, Ut.batch_extension())
        Ut.stardog_on(bat_path)

        print "LISTENING AT: {}...".format(Svr.settings[St.stardog_data_path])
        Ut.listening(Svr.settings[St.stardog_data_path])

    app.run(host="0.0.0.0", port=5077)
