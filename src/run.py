from app import app
import os
import requests
import Alignments.Settings as St
import Alignments.Utility as Ut
import Alignments.Server_Settings as Svr

# https://github.com/CLARIAH/grlc/blob/master/docker-assets/entrypoint.sh
# https://github.com/CLARIAH/grlc/blob/master/gunicorn_config.py
# https://docupub.com/pdfmerge/
print "\nRUNNING THE LENTICULAR LENS SERVER"
lock_file = None
if __name__ == "__main__":

    try:
        lock_file = [name for name in os.listdir(Svr.settings[St.stardog_data_path]) if name.endswith('.lock')]
        # print lock_file
    except Exception as err:
        print str(err)

    if lock_file is not None:

        try:
            response = requests.get("http://{}".format(Svr.settings[St.stardog_host_name]))
            # response = Qry.endpoint("SELECT * {?sub ?obj ?pred} LIMIT 1")

        except Exception as err:
            response = str(err)

        # print response
        if str(response).__contains__("401"):
            print "THE STARDOG SERVER IS ON AND REQUIRES PASSWORD."

        elif len(lock_file) > 0 and (
                    str(response).__contains__("200") or
                    str(response).__contains__("401") or
                    str(response).__contains__("No connection") is False):
            print "THE STARDOG SERVER IS ALREADY ON."

        else:
            print "\n>>> ", response
            "SWITCHING ON THE SERVER..."
            bat_path = "{}stardogStart{}".format(Svr.SRC_DIR, Ut.batch_extension())
            Ut.stardog_on(bat_path)

            print "LISTENING AT: {}...".format(Svr.settings[St.stardog_data_path])
            Ut.listening(Svr.settings[St.stardog_data_path])

        app.run(host="0.0.0.0", port=int(os.getenv("LL_PORT", 5077)))

# LL_PORT=5077 LL_STARDOG_DATABASE="risis" python run.py
