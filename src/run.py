from app import app
import os
import requests
import webbrowser as web
import Alignments.Settings as St
import Alignments.Utility as Ut
import Alignments.Server_Settings as Svr

# https://github.com/CLARIAH/grlc/blob/master/docker-assets/entrypoint.sh
# https://github.com/CLARIAH/grlc/blob/master/gunicorn_config.py
# https://docupub.com/pdfmerge/
print "\nRUNNING THE LENTICULAR LENS SERVER"
lock_file = None
RESET_SERVER_BATS = False
if __name__ == "__main__":

    try:

        if RESET_SERVER_BATS is True:
            START_path = "{}stardogStart{}".format(Svr.SRC_DIR, Ut.batch_extension())
            STOP_path = "{}stardogStop{}".format(Svr.SRC_DIR, Ut.batch_extension())
            if os.path.exists(START_path) is True:
                os.remove(START_path)
            if os.path.exists(STOP_path) is True:
                os.remove(STOP_path)

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

        # CREATING THE DATABASE IN STARDOG
        db_bat_path = "{}stardogCreate_{}_db{}".format(Svr.SRC_DIR, Svr.settings[St.database], Ut.batch_extension())
        Ut.create_database(Svr.settings[St.stardog_path], db_bat_path, db_name=Svr.settings[St.database])

        print "LAUNCHING THE LENTICULAR LENS ON YOUR DEFAULT BROWSER AT PORT: {}".format(Svr.settings[St.ll_port])
        web.open_new_tab('http://localhost:{}/'.format(Svr.settings[St.ll_port]))
        app.run(host="0.0.0.0", port=Svr.settings[St.ll_port])

# LL_PORT=5077 LL_STARDOG_DATABASE="risis" python run.py
