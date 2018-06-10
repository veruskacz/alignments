import os
import re
import sys
import time
import datetime
import platform
import fileinput
import subprocess
from cmd import Cmd
from os.path import join
import cStringIO as Buffer

# #####################################################
""" FUNCTION PARAMETERS """
# #####################################################

OPE_SYS = platform.system().lower()
_format = "%a %b %d %H:%M:%S %Y"
date = datetime.datetime.today()
begining = time.time()
highlight = "---------------------------------------------------"
_line = "--------------------------------------------------------------" \
        "--------------------------------------------------------------"

# CLEAR SHELL
if OPE_SYS == "windows":
    os.system('cls')
else:
    os.system('clear')

print "\n{}\n{:>117}\n{}\n".format(_line, date.strftime(_format), _line)
commands = {

    "versions": """
    git --version
    pip --version
    python --version
    virtualenv --version
    """,

    "git_v": "git --version",
    "pip_v": "pip --version",
    "pyt_v": "python --version",
    "env_v": "virtualenv --version",

    "pip": "easy_install pip==10.0.1",

    "pip_up": "sudo python -m pip install --upgrade --force-reinstall pip",

    "venv": "pip install virtualenv",

    "git_clone": """
    echo "CLONING THE LENTICULAR LENS SOFTWARE"
    git clone https://github.com/veruskacz/alignments.git {0}
    """,

    "git_pull": """
    cd {0}
    git reset --hard HEAD
    git pull
    """,

    "windows": """
    cls
    echo "    >>> UPGRADING PIP"
    python -m pip install --upgrade pip

    echo "   >>> CLONING THE LENTICULAR LENS SOFTWARE"
    echo git clone https://github.com/alkoudouss/alignments.git {0}

    echo "   >>> CREATING A VIRTUAL ENVIRONMENT"
    virtualenv  --python={2}{1}python.exe {0}

    echo "   >>> ACTIVATING THE VIRTUAL ENVIRONMENT"
    call {0}{1}Scripts{1}activate.bat

    echo "   >>> INSTALLING THE LENTICULAR LENS REQUIREMENTS"
    pip install -r  {0}{1}requirements.txt

    echo "   >>> INSTALLATION DONE..."
    echo "   >>> RUNNING THE LENTICULAR LENS"
    cd {0}{1}src
    echo "python -c "import webbrowser as web; web.open_new_tab('http://localhost:5077/')""
    python run.py
    """,

    "mac": """
    clear
    echo "    >>> UPGRADING PIP"
    sudo python -m pip install --upgrade pip

    echo "   >>> CLONING THE LENTICULAR LENS SOFTWARE"
    echo git clone https://github.com/alkoudouss/alignments.git {0}

    echo "   >>> CREATING A VIRTUAL ENVIRONMENT"
    virtualenv  --python={2} {0}

    echo "   >>> ACTIVATING THE VIRTUAL ENVIRONMENT"
    source {0}{1}bin{1}activate

    echo "   >>> INSTALLING THE LENTICULAR LENS REQUIREMENTS"
    sudo pip install -r  {0}{1}requirements.txt

    echo "   >>> INSTALLATION DONE..."
    echo "   >>> RUNNING THE LENTICULAR LENS"
    cd {0}{1}src
    echo "   >>> mac: LL_STARDOG_PATH=\\\"{3}\\\" LL_STARDOG_DATA=\\\"{4}\\\" python run.py"
    echo "python -c \\\"import webbrowser as web; web.open_new_tab(\\\'http://localhost:5077/\\\')\\\""
    python run.py
    """,

    "runMac": """
    echo "   >>> ACTIVATING THE VIRTUAL ENVIRONMENT"
    source {0}{1}bin{1}activate

    echo "   >>> RUNNING THE LENTICULAR LENS"
    cd {0}{1}src
    python run.py
    """,

    "runWin": """
    echo "   >>> ACTIVATING THE VIRTUAL ENVIRONMENT"
    call {0}{1}Scripts{1}activate.bat

    echo "   >>> RUNNING THE LENTICULAR LENS"
    cd {0}{1}src
    python run.py
    """
}


# #####################################################
""" INPUT PROMPT CLASS """
# #####################################################


def process_input(prompt):

    try:
        return input("{:60} : ".format(prompt))
    except Exception as err:
        while True:
            try:
                print "\n\tENTER THE INPUT WITHIN QUOTES"
                return input("{:60} : ".format(prompt))
            except Exception as err:
                "nothing"


def prompts():
    directory = process_input("    Enter the [INSTALLATION DIRECTORY] path")
    python_path = process_input("    Enter the [PYTHON DIRECTORY] path")
    stardog_bin = process_input("    Enter the [STARDOG BIN DIRECTORY] path")
    stardog_home = process_input("    Enter [STARDOG HOME DIRECTORY] path")
    database_name = process_input("    Enter the [STARDOG DATABASE NAME]")
    run = process_input("    Enter True/False if you want to [RUN] this program")
    port = process_input("    Enter a new [PORT] if needed. THE DEAFULT IS 5077")
    if isinstance(port.strip(), (int, long)) is False:
        port = "5077"

    return (directory, python_path, stardog_bin, stardog_home, database_name, run, port)


class LLPrompt(Cmd):

    message = """
    Lenticular Lens Installation Prompt...

        OPTION 1. QUIT
            Enter [1] or [quit] to exit

        OPTION 2. STEP-BY-STEP SHELL-INSTALL
            Enter [2] or [install] for directly inserting the required input parameters from the [cmd-shell].

        OPTION 3. ALL-IN INSTALL
            Enter [3] or [install all] to run the code using the [parameter_input] edited within the file.

        OPTION 4. RUN THE LENTICUALR LENS
            Enter [4] or [run] to run the Lenticular Lens. This onption is used only after an installation.
            Enter [4 port] or [run port] to run the Lenticular Lens on a port of your choosing.

        OPTION 5. UPDATE THE TOOL VERSION FROM GIT AND RUN THE LENTICUALR LENS
            Enter [5] or [runpull] to run the Lenticular Lens. This onption is used only after an installation.
            Enter [5 port] or [runpull port] to run the Lenticular Lens on a port of your choosing.\n
    """

    def do_clear(self):
        os.system('cls')

    # QUIT THE LENTICIULAR LENS WITH OPTION [1]
    def do_1(self, args):
        """Quits the program."""
        print "{}\n{:>117}\n{}".format(_line, "Thanks for trying it!.", _line)
        raise SystemExit

    # QUIT THE LENTICIULAR LENS WITH OPTION [QUIT]
    def do_quit(self, args):
        """Quits the program."""
        print "{}\n{:>117}\n{}".format(_line, "Thanks for trying it!.", _line)
        raise SystemExit

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    2. INSTALL THE REQUIREMENTS USING THE COMMAND SHELL STEP-BYSTEP
       PULL THE LATEST VERSION AND
       RUN THE LENTICULAR LENS
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    # INSTALL USING THE SHELL PROMPT
    def do_2(self, args):

        if len(args) == 0:
            (directory, python_path, stardog_bin, stardog_home, database_name, run, port) = prompts()
            install_pronpt(directory, python_path, stardog_bin, stardog_home, database_name, run, port)


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    3. INSTALL THE REQUIREMENTS USING THE ALL-IN-ONE OPTION BASED
       ON THE PARAMETERS INSERTED
       PULL THE LATEST VERSION AND
       RUN THE LENTICULAR LENS
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    # INSTALL USING THE EDITED INPUT PARAMETERS
    def do_3(self, args):
        install(parameter_input)


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    4. RUN THE LENTICULAR LENS WITHOUT A GIT PULL
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    # RUN THE LENTICULAR LENS WITH THE [4] OPTION
    def do_4(self, port):

        overwright = False
        parameters = input_prep(parameter_input)
        directory = parameters[0]
        # python_path = parameters[1]
        stardog_bin = parameters[2]
        stardog_home = parameters[3]
        database_name = parameters[4]
        # run = parameters[5]

        # SETTING HE LL PORT
        if len(port) > 0:
            try:
                int(str(port))
                ll_port = port
                overwright = True
                print "\n\t>>> {:18} : PORT [{}] REPLACED BY PORT [{}]".format("PORT OVERWRITING", parameters[6], port)
            except:
                ll_port = parameters[6]
        else:
            ll_port = parameters[6]

        file_path = join(directory, "INSTALLATION.bat") if OPE_SYS == 'windows' else join(directory, "INSTALLATION.sh")
        w_dir = join(directory, "alignments")


        print "\nYOU HAVE OPT FOR DIRECTLY RUNNING THE LENTICULAR LENS."

        try:
            # RUNS IN A NEW SHELL
            cmd = commands["runWin"] if OPE_SYS == 'windows' else commands["runMac"]
            cmd = cmd.format(w_dir, os.path.sep)
            print cmd

            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 7. UPDAT THE SEVER SETTINGS WITH STARDOG HOME AND BIN PATHS
            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            print "\n{0}\n    >>> UPDATING SERVER SETTINGS\n{0}\n".format(highlight)
            update_settings(directory, stardog_home, stardog_bin, database_name, ll_port)

            # RUN THE LENTICULAR LENS
            execute_cmd(cmd=cmd, file_path=file_path, output=False)

        except Exception as err:
            print err.message
            print "ERROR"
            return err.message

    # RUN THE LENTICULAR LENS WITH THE [RUN] OPTION
    def do_run(self, port):
        overwright = False
        parameters = input_prep(parameter_input)
        directory = parameters[0]
        # python_path = parameters[1]
        stardog_bin = parameters[2]
        stardog_home = parameters[3]
        database_name = parameters[4]
        # run = parameters[5]
        if len(port) > 0:
            try:
                int(str(port))
                ll_port = port
                overwright = True
                print "\n\t>>> {:18} : PORT [{}] REPLACED BY PORT [{}]".format("PORT OVERWRITING", parameters[6], port)
            except:
                ll_port = parameters[6]
        else:
            ll_port = parameters[6]

        file_path = join(directory, "INSTALLATION.bat") if OPE_SYS == 'windows' else join(directory, "INSTALLATION.sh")
        w_dir = join(directory, "alignments")
        # cmds = commands["windows"].format(w_dir, os.path.sep, python_path, stardog_bin, stardog_home)

        print "\nYOU HAVE OPT FOR DIRECTLY RUNNING THE LENTICULAR LENS."
        try:
            # RUNS IN A NEW SHELL
            cmd = commands["runWin"] if OPE_SYS == 'windows' else commands["runMac"]
            cmd = cmd.format(w_dir, os.path.sep)
            print cmd

            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 7. UPDAT THE SEVER SETTINGS WITH STARDOG HOME AND BIN PATHS
            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            print "\n{0}\n    >>> UPDATING SERVER SETTINGS\n{0}\n".format(highlight)
            update_settings(directory, stardog_home, stardog_bin, database_name, ll_port)

            execute_cmd(cmd=cmd, file_path=file_path, output=False)

        except Exception as err:
            print err.message
            print "ERROR"
            return err.message


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    5. PULL THE LATEST VERSION AND RUN THE LENTICULAR LENS
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    def do_5(self, port):

        overwright = False
        parameters = input_prep(parameter_input)
        directory = parameters[0]
        # python_path = parameters[1]
        stardog_bin = parameters[2]
        stardog_home = parameters[3]
        database_name = parameters[4]
        run = parameters[5]

        # SETTING HE LL PORT
        if len(port) > 0:
            try:
                int(str(port))
                ll_port = port
                overwright = True
                print "\n\t>>> {:18} : PORT [{}] REPLACED BY PORT [{}]".format("PORT OVERWRITING", parameters[6],
                                                                               port)
            except:
                ll_port = parameters[6]
        else:
            ll_port = parameters[6]

        file_path = join(directory, "INSTALLATION.bat") if OPE_SYS == 'windows' else join(directory,
                                                                                          "INSTALLATION.sh")
        w_dir = join(directory, "alignments")

        print "\nYOU HAVE OPT FOR DIRECTLY RUNNING THE LENTICULAR LENS."

        try:
            # RUNS IN A NEW SHELL
            cmd = commands["runWin"] if OPE_SYS == 'windows' else commands["runMac"]
            cmd = cmd.format(w_dir, os.path.sep)
            print cmd

            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 7. UPDAT THE SEVER SETTINGS WITH STARDOG HOME AND BIN PATHS
            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            print "\n{0}\n    >>> UPDATING SERVER SETTINGS\n{0}\n".format(highlight)
            update_settings(directory, stardog_home, stardog_bin, database_name, ll_port)

            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 2.3 CLONE OR PULTHE LENTICULAR LENS SOFTWARE
            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            if os.path.isdir(join(directory, "alignments")) is False:
                print "\n{0}\n    >>> LENTICULAR LENS CLONE REQUEST\n{0}\n".format(highlight)
                cloning = commands["git_clone"].format(w_dir)
                execute_cmd(cloning, file_path, output=False, run=run)
            else:
                print "\n{0}\n    >>> LENTICULAR LENS PULL REQUEST\n{0}\n".format(highlight)
                pulling = commands["git_pull"].format(join(directory, "alignments"))
                execute_cmd(pulling, file_path, output=False, run=run)

            # RUN THE LENTICULAR LENS
            execute_cmd(cmd=cmd, file_path=file_path, output=False)

        except Exception as err:
            print err.message
            print "ERROR"
            return err.message

    def do_runpull(self, port):

        overwright = False
        parameters = input_prep(parameter_input)
        directory = parameters[0]
        # python_path = parameters[1]
        stardog_bin = parameters[2]
        stardog_home = parameters[3]
        database_name = parameters[4]
        run = parameters[5]

        # SETTING HE LL PORT
        if len(port) > 0:
            try:
                int(str(port))
                ll_port = port
                overwright = True
                print "\n\t>>> {:18} : PORT [{}] REPLACED BY PORT [{}]".format("PORT OVERWRITING", parameters[6],
                                                                               port)
            except:
                ll_port = parameters[6]
        else:
            ll_port = parameters[6]

        file_path = join(directory, "INSTALLATION.bat") if OPE_SYS == 'windows' else join(directory,
                                                                                          "INSTALLATION.sh")
        w_dir = join(directory, "alignments")

        print "\nYOU HAVE OPT FOR DIRECTLY RUNNING THE LENTICULAR LENS."

        try:
            # RUNS IN A NEW SHELL
            cmd = commands["runWin"] if OPE_SYS == 'windows' else commands["runMac"]
            cmd = cmd.format(w_dir, os.path.sep)
            print cmd

            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 7. UPDAT THE SEVER SETTINGS WITH STARDOG HOME AND BIN PATHS
            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            print "\n{0}\n    >>> UPDATING SERVER SETTINGS\n{0}\n".format(highlight)
            update_settings(directory, stardog_home, stardog_bin, database_name, ll_port)

            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 2.3 CLONE OR PULTHE LENTICULAR LENS SOFTWARE
            """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            if os.path.isdir(join(directory, "alignments")) is False:
                print "\n{0}\n    >>> LENTICULAR LENS CLONE REQUEST\n{0}\n".format(highlight)
                cloning = commands["git_clone"].format(w_dir)
                execute_cmd(cloning, file_path, output=False, run=run)
            else:
                print "\n{0}\n    >>> LENTICULAR LENS PULL REQUEST\n{0}\n".format(highlight)
                pulling = commands["git_pull"].format(join(directory, "alignments"))
                execute_cmd(pulling, file_path, output=False, run=run)

            # RUN THE LENTICULAR LENS
            execute_cmd(cmd=cmd, file_path=file_path, output=False)

        except Exception as err:
            print err.message
            print "ERROR"
            return err.message

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DO OPTION 3 OR 4
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    # THIS GIVES BOTH OPTIONS
    def do_install(self, args):

        if len(args) == 0:
            (directory, python_path, stardog_bin, stardog_home, database_name, run, port) = prompts()
            install_pronpt(directory, python_path, stardog_bin, stardog_home, database_name, run, port)
        else:
            install(parameter_input)


# #####################################################
""" INSTALLATION HELPER FUNCTIONS """
# #####################################################


def versions(file_path):
    pattern = "([\d*\.]+)"
    import sys
    # print(sys.version)

    try:
        git_out = execute_cmd(commands["git_v"], file_path, output=True)
        git = re.findall('git version (.+)', str(git_out))
        if len(git) == 0:
            git = ["0"]
    except:
        git = ["0"]

    try:
        pyt_out =  subprocess.check_output(commands["pyt_v"], shell=True, stderr=subprocess.STDOUT)
        python = re.findall('python {}'.format(pattern), str(pyt_out), flags=re.IGNORECASE)
        if len(python) == 0:
            python = ["0"]
    except Exception as err:
        python = ["0"]

    try:
        pip_out = execute_cmd(commands["pip_v"], file_path, output=True)
        pip = re.findall('pip {}'.format(pattern), str(pip_out))
        if len(pip) == 0:
            pip = ["0"]
    except:
        pip = ["0"]

    try:
        env_out = execute_cmd(commands["env_v"], file_path, output=True)
        env = re.findall('{}[\n]*'.format(pattern), env_out)
        if len(env) == 0:
            env = ["0"]
        # print env_out, "ENV", env
    except:
        env = ["0"]

    return (git, python, pip, env)


def install_package(package, command, condition, condition_idx, file_path):

    package = str(package).upper()
    while condition[condition_idx][0] == "0":
        print("\n\t>>> THE REQUIRED [{}] VERSION IS NOT INSTALLED!".format(package))
        proceed = process_input("\t\tEnter [1] to INSTALL [{}] or enter [anything else] to exit.".format(package))
        if str(proceed).strip() == "1":
            if OPE_SYS == 'windows':
                execute_cmd(cmd=commands[command], file_path=file_path, output=False)
            else:
                execute_cmd(cmd="sudo " + commands[command], file_path=file_path, output=False)
            # print requirements_out
            condition = versions(file_path)
        else:
            print "\t\tFORCED EXIT BY USER."
            exit(1)


def execute_cmd(cmd, file_path=None, output=True, run=True):

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # CREATE THE BATCH FILE FOR CHECKING PIP PYTHON AND VIRTUALENV
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    if file_path is not None:
        with open(name=file_path, mode="wb") as writer:
            writer.write(cmd)

        # MAC PERMISSION ISSUES
        if OPE_SYS != 'windows':
            os.chmod(file_path, 0o777)

    # EXECUTE THE COMMAND
    if run is True:

        try:
            if output is True:
                output = subprocess.check_output(file_path, shell=True, stderr=subprocess.STDOUT)
                return str(output)
            else:
                # RUNS IN A NEW SHELL
                subprocess.call(file_path, shell=True)

        except Exception as err:
            return err.message


def normalise_path(file_path):

    """""""""""""""""""""""""""
    # NORMALISES WINDOWS PATH
    """""""""""""""""""""""""""
    file_path = re.sub('[\1]', "\\\\1", file_path)
    file_path = re.sub('[\2]', "\\\\2", file_path)
    file_path = re.sub('[\3]', "\\\\3", file_path)
    file_path = re.sub('[\4]', "\\\\4", file_path)
    file_path = re.sub('[\5]', "\\\\5", file_path)
    file_path = re.sub('[\6]', "\\\\6", file_path)
    file_path = re.sub('[\7]', "\\\\7", file_path)
    file_path = re.sub('[\0]', "\\\\0", file_path)
    file_path = re.sub('[\a]', "\\\\a", file_path)
    file_path = re.sub('[\b]', "\\\\b", file_path)
    file_path = re.sub('[\f]', "\\\\f", file_path)
    file_path = re.sub('[\n]', "\\\\n", file_path)
    file_path = re.sub('[\r]', "\\\\r", file_path)
    file_path = re.sub('[\t]', "\\\\t", file_path)
    file_path = re.sub('[\v]', "\\\\v", file_path)
    return file_path


def replace_all(file_path, search_exp, replace_exp):

    """""""""""""""""""""""""""""""""""""""""""""""
    # REPLACES AN EXPRESSION IN THE SPECIFIED FILE
    """""""""""""""""""""""""""""""""""""""""""""""

    wr = Buffer.StringIO()
    if os.path.isfile(file_path) is False:
        print "THE PROVIDED FILE BELOW DOES NOT EXIST" \
              "\n\t>>> {}\nFOR THAT YOUR ACTION HAS BEEN TERMINATED\n".format(file_path)
        exit(0)

    with open(name=file_path, mode="r") as reader:
        for line in reader:
            found = re.findall(search_exp, line)
            if len(found) > 0:
                print "\t{:50} <-- {}".format(found[0], replace_exp)
                replaced = line.replace(found[0], replace_exp)
                wr.write(replaced)
            else:
                wr.write(line)

    with open(name=file_path, mode="w+") as writer:
        writer.write(wr.getvalue())


def update_settings(directory, stardog_home, stardog_bin, database_name, ll_port):

    """""""""""""""""""""""""""""""""""""""""""""""""""""
    # UPDATING THE SETTINGS IN THE SERVER SETTING FILE
    """""""""""""""""""""""""""""""""""""""""""""""""""""

    svr_settings = join(directory, "alignments{0}src{0}Alignments{0}Server_Settings.py".format(os.path.sep))

    # STARDOG BIN
    s_bin = """\"LL_STARDOG_PATH",[ ]*"(.*)\""""
    replace_all(svr_settings, s_bin, """{0}""".format(stardog_bin, os.path.sep))

    # STARDOG DATA OF HOME
    s_data = """"LL_STARDOG_DATA",[ ]*"(.*)\""""
    replace_all(svr_settings, s_data, """{}""".format(stardog_home))

    # LENTICULAR LENS DATABASE NAME
    d_data = """"LL_STARDOG_DATABASE",[ ]*"(.*)\""""
    replace_all(svr_settings, d_data, """{}""".format(database_name))

    # LENTICULAR LENS POERT
    # port = """"LL_PORT",[ ]*(\d*)"""
    # replace_all(svr_settings, port, """{}""".format(ll_port))
    # Svr.settings[St.ll_port] = ll_port
    os.environ['LL_PORT'] = str(ll_port)


# #####################################################
""" INSTALLATION ALL IN ONE """
# #####################################################


def input_prep(parameter_inputs):

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # PREPARING THE INPUT PARAMETRS AS IT IS GEVEN AS A STRING
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    # INPUT EXTRACTIOIN STEP 1
    inputs_0 = re.findall("run[ ]*=[ ]*([^\"\'\n]+)", parameter_inputs)
    inputs_1 = re.findall("directory[ ]*=[ \"\']*([^\"\'\n]+)", parameter_inputs)
    inputs_2 = re.findall("python_path[ ]*=[ \"\']*([^\"\'\n]+)", parameter_inputs)
    inputs_3 = re.findall("stardog_bin[ ]*=[ \"\']*([^\"\'\n]*)", parameter_inputs)
    inputs_4 = re.findall("stardog_home[ ]*=[ \"\']*([^\"\'\n]*)", parameter_inputs)
    inputs_5 = re.findall("database_name[ ]*=[ \"\']*([^\"\'\n]*)", parameter_inputs)
    inputs_6 = re.findall("ll_port[ ]*=[ \"\']*([^\"\'\n]*)", parameter_inputs)

    #  INPUT EXTRACTIOIN STEP 2
    run = bool(str(inputs_0[0]).strip()) if len(inputs_0) > 0 else None
    directory = normalise_path(str(inputs_1[0]).strip()) if len(inputs_1) > 0 else None
    python_path = normalise_path(str(inputs_2[0]).strip()) if len(inputs_2) > 0 else None
    stardog_bin = normalise_path(str(inputs_3[0]).strip()) if len(inputs_3) > 0 else None
    stardog_home = normalise_path(str(inputs_4[0]).strip()) if len(inputs_4) > 0 else None
    database_name = str(inputs_5[0]).strip() if len(inputs_5) > 0 else None
    ll_port = int(inputs_6[0].strip()) if len(inputs_6) > 0 else 5077

    # PRINTING THE EXTRACTED INPUTS
    print "\nSTARTING THE INSTALLATION OF THE LENTICULAR LENS"
    print "\n1. INPUTS"
    print "\n\t{:23}: {}".format("INSTALLATION DIRECTORY", directory)
    print "\t{:23}: {}".format("INSTALLED PYTHON PATH", python_path)
    print "\t{:23}: {}".format("STARDOG DATA PATH", stardog_home)
    print "\t{:23}: {}".format("STARDOG HOME PATH", stardog_bin)
    print "\t{:23}: {}".format("DATABASE NAME", database_name)
    if run is True:
        print "\t{:23}: {} at PORT {}".format("RUN", run, ll_port)
    else:
        print "\t{:23}: {}".format("RUN", run)

    # CHECKING IF ALL INPUTS HAVE BEEN PROVIDED
    if run is None or directory is None or python_path is None or stardog_bin is None or \
                    stardog_home is None or database_name is None:
        print "\nCHECK THE ENTERED INPUTS.... THERE MAY BE MISSING OR MAY NOT BE A PROPER PATH."
        exit(0)

    # MAC INPUT ARE NOT WITH BACKSLASH
    if OPE_SYS != "windows":
        if directory.__contains__("\\") or python_path.__contains__("\\") or stardog_bin.__contains__("\\") or \
                        stardog_home.__contains__("\\") is None:
            print "\nCHECK YOUR INPUT PATHS AGAIN AS IT LOOKS LIKE A WINDOWS PATH :-)\n"
            exit(0)

    # ENV VARIABLE OR PROPER VARIABLE ARE ALLOWED
    directory = os.getenv("LL_DIRECTORY", directory)
    python_path = os.getenv("LL_PYTHON_PATH", python_path)
    stardog_bin = os.getenv("LL_STARDOG_PATH", stardog_bin)
    stardog_home = os.getenv("LL_STARDOG_DATA", stardog_home)
    database_name = os.getenv("LL_STARDOG_DATABASE", database_name)

    # MAKING SURE THAT THE PATHS END PROPERLY
    if OPE_SYS != "windows":
        stardog_bin = "{}/".format(stardog_bin) if stardog_bin.endswith("/") is False else stardog_bin
        stardog_home = "{}/".format(stardog_home) if stardog_home.endswith("/") is False else stardog_home
    else:
        stardog_bin = "{}\\".format(stardog_bin) if stardog_bin.endswith("\\") is False else stardog_bin
        stardog_home = "{}\\".format(stardog_home) if stardog_home.endswith("\\") is False else stardog_home
        directory = directory.replace("\\", "\\\\")
        python_path = python_path.replace("\\", "\\\\")
        stardog_bin = stardog_bin.replace("\\", "\\\\")
        stardog_home = stardog_home.replace("\\", "\\\\")

    return [directory, python_path, stardog_bin, stardog_home, database_name, run, ll_port]


def install(parameter_inputs):

    """""""""""""""""""""""""""
    # INSTALLATION MAIN ENTRY
    """""""""""""""""""""""""""

    parameters = input_prep(parameter_inputs)
    directory = parameters[0]
    python_path = parameters[1]
    stardog_bin = parameters[2]
    stardog_home = parameters[3]
    database_name = parameters[4]
    run = parameters[5]
    ll_port = parameters[6]

    # RUNNING THE GENERIC INSTALLATION
    generic_install(directory, python_path, stardog_home, stardog_bin, database_name, run=run, ll_port=ll_port)

    # RUNNING WINDOWS SPECIFIC INSTALLATION
    if OPE_SYS == "windows":
        win_install(directory, python_path, stardog_home=stardog_home, stardog_bin=stardog_bin, run=run)

    # RUNNING MAC OR LINUX SPECIFIC INSTALLATION
    else:
        mac_install(directory, python_path, stardog_home=stardog_home, stardog_bin=stardog_bin, run=run)


# #####################################################
""" INSTALLATION STEP-BYSTEP WITH PROMPT """
# #####################################################


def input_prompt_prep(directory, python_path, stardog_bin, stardog_home, database_name, run, ll_port):

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # PREPARING THE INPUT PARAMETRS AS IT IS GEVEN AS A STRING
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    #  INPUT EXTRACTIOIN STEP 2
    run = bool(run) if len(str(run)) > 0 else None
    directory = normalise_path(directory.strip()) \
        if len(directory) > 0 and directory.__contains__(os.path.sep) else None

    python_path = normalise_path(python_path.strip()) \
        if len(python_path) > 0 and python_path.__contains__(os.path.sep) else None

    stardog_bin = normalise_path(stardog_bin.strip()) \
        if len(stardog_bin) > 0 and stardog_bin.__contains__(os.path.sep) else None

    stardog_home = normalise_path(stardog_home.strip()) \
        if len(stardog_home) > 0  and stardog_home.__contains__(os.path.sep) else None

    database_name = database_name.strip() if len(database_name) > 0  else None

    ll_port = int(str(ll_port).strip()) if isinstance( ll_port.strip(), (int, long)) else 5077


    # PRINTING THE EXTRACTED INPUTS
    print "\nSTARTING THE INSTALLATION OF THE LENTICULAR LENS"
    print "\n1. INPUTS"
    print "\n\t{:23}: {}".format("INSTALLATION DIRECTORY", directory)
    print "\t{:23}: {}".format("INSTALLED PYTHON PATH", python_path)
    print "\t{:23}: {}".format("STARDOG DATA PATH", stardog_home)
    print "\t{:23}: {}".format("STARDOG HOME PATH", stardog_bin)
    print "\t{:23}: {}".format("DATABASE NAME", database_name)
    if run is True:
        print "\t{:23}: {} at PORT {}".format("RUN", run, ll_port)
    else:
        print "\t{:23}: {}".format("RUN", run)

    # CHECKING IF ALL INPUTS HAVE BEEN PROVIDED
    if run is None or directory is None or python_path is None or stardog_bin is None or \
                    stardog_home is None or database_name is None:
        print "\nCHECK THE ENTERED INPUTS.... THERE MAY BE MISSING OR MAY NOT BE A PROPER PATH."
        exit(0)

    # MAC INPUT ARE NOT WITH BACKSLASH
    if OPE_SYS != "windows":
        if directory.__contains__("\\") or python_path.__contains__("\\") or stardog_bin.__contains__("\\") or \
                        stardog_home.__contains__("\\") is None:
            print "\nCHECK YOUR INPUT PATHS AGAIN AS IT LOOKS LIKE A WINDOWS PATH :-)\n"
            exit(0)

    # ENV VARIABLE OR PROPER VARIABLE ARE ALLOWED
    directory = os.getenv("LL_DIRECTORY", directory)
    python_path = os.getenv("LL_PYTHON_PATH", python_path)
    stardog_bin = os.getenv("LL_STARDOG_PATH", stardog_bin)
    stardog_home = os.getenv("LL_STARDOG_DATA", stardog_home)
    database_name = os.getenv("LL_STARDOG_DATABASE", database_name)

    # MAKING SURE THAT THE PATHS END PROPERLY
    if OPE_SYS != "windows":
        stardog_bin = "{}/".format(stardog_bin) if stardog_bin.endswith("/") is False else stardog_bin
        stardog_home = "{}/".format(stardog_home) if stardog_home.endswith("/") is False else stardog_home
    else:
        stardog_bin = "{}\\".format(stardog_bin) if stardog_bin.endswith("\\") is False else stardog_bin
        stardog_home = "{}\\".format(stardog_home) if stardog_home.endswith("\\") is False else stardog_home
        directory = directory.replace("\\", "\\\\")
        python_path = python_path.replace("\\", "\\\\")
        stardog_bin = stardog_bin.replace("\\", "\\\\")
        stardog_home = stardog_home.replace("\\", "\\\\")

    return [directory, python_path, stardog_bin, stardog_home, database_name, run, ll_port]


def install_pronpt(directory, python_path, stardog_bin, stardog_home, database_name, run, ll_port):

    """""""""""""""""""""""""""
    # INSTALLATION MAIN ENTRY
    """""""""""""""""""""""""""

    # RUNNING THE GENERIC INSTALLATION
    parameters = input_prompt_prep(directory, python_path, stardog_bin, stardog_home, database_name, run, ll_port)
    directory = parameters[0]
    python_path = parameters[1]
    stardog_bin = parameters[2]
    stardog_home = parameters[3]
    database_name = parameters[4]
    run = parameters[5]
    ll_port = parameters[6]

    # RUNNING THE GENERIC INSTALLATION
    generic_install(directory, python_path, stardog_home, stardog_bin, database_name, run=run, ll_port=ll_port)

    # RUNNING WINDOWS SPECIFIC INSTALLATION
    if OPE_SYS == "windows":
        win_install(directory, python_path, stardog_home=stardog_home, stardog_bin=stardog_bin, run=run)

    # RUNNING MAC OR LINUX SPECIFIC INSTALLATION
    else:
        mac_install(directory, python_path, stardog_home=stardog_home, stardog_bin=stardog_bin, run=run)


# #####################################################
""" INSTALLATION: PLATFORM INDEPENDENT DEPENDENT """
# #####################################################


def generic_install(directory, python_path, stardog_home, stardog_bin, database_name, run=False, ll_port=5077):

    print "\n2. VERSIONS\n\n\t{:23}: {}".format("COMPUTER TYPE", platform.system().upper())

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # 2.1 CHECK WHETHER THE INSTALLATION DIRECTORY EXISTS
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    if os.path.isdir(directory) is False:
        try:
            os.mkdir(directory)
            print "\nTHE PROVIDED DIRECTORY DID NOT EXIST BUT WAS CREATED\n"
        except Exception as err:
            print "\nTHE PROVIDED DIRECTORY COULD NOT BE CREATED\n"
            print err
            exit(0)
    # 2. INSTALLATION BATCH FILE PATH
    w_dir = join(directory, "alignments")
    file_path = join(directory, "INSTALLATION.bat" if OPE_SYS == "windows" else "INSTALLATION.sh")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # 2.2 CHECKING THE AVAILABLE VESIONS OF THE REQUIRED PAKAGES
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    (git, python, pip, env) = versions(file_path)
    # print (git, python, pip, env)

    # ###############################
    # PYTHON
    # ###############################
    if python[0] == "0":
        print("\n\t>>> MAKE SURE YOU HAVE INSTALLED THE REQUIRED [PYTHON] VERSION")
        exit(1)

    # P-1.PACKAGE MANAGEMENT SYSTEM
    install_package(package="PIP", command="pip",
                    condition=(git, python, pip, env), condition_idx=2, file_path=file_path)

    # BETTING THE PIP VERSION AS INTEGER
    pip_version = int(str(pip[0]).replace(".", "")) if len(pip) > 0 else 0
    # print pip_version
    if pip_version > 1000:
        # PIP VERSION IS OKAY
        print "\t{:23}: {}".format("PIP VERSION", pip[0])
    else:
        # UPGRADING PIP
        requirements_out = execute_cmd(cmd=commands["pip_up"], file_path=file_path)
        print requirements_out

    # ###############################
    # VIRTUAL ENVIRONMENT
    # ###############################
    install_package(package="VIRTUALENV", command="venv",
                    condition=(git, python, pip, env), condition_idx=3, file_path=file_path)

    # ###############################
    # 4. GIT VERSION IS REQUIRED
    # ###############################
    # git version 2.10.1.windows.1
    git_version = git[0][0] if len(git) > 0 else 0
    if int(git_version[0]) == 0:
        print "\n\t>>> YOU NEED TO INSTALL GIT FROM [https://git-scm.com/downloads]\n"
        exit(0)
    elif int(git_version[0]) <= 1:
        print "\n\t>>>YOU NEED TO UPGRADE YOUR GIT FROM [https://git-scm.com/downloads]\n"
        exit(0)
    print "\t{:23}: {}".format("GIT VERSION", git[0])

    # ###############################
    # 5. PYTHON VERSION IS REQUIRED
    # ###############################
    pattern = "([\d*\.]+)"
    python_version = int(str(python[0]).replace(".", "")) if len(python) > 0 else 0
    if (python_version >= 27) and (python_version < 2713):

        print "\t{:23}: {}".format("PYTHON VERSION", python[0])

        # ###############################
        # MAKE SURE PIP IS INSTALL
        # ###############################
        pip_version = int(str(pip[0]).replace(".", "")) if len(pip) > 0 else 0
        # print pip_version
        if pip_version > 1000:
            print "\t{:23}: {}".format("PIP VERSION", pip[0])
        else:
            # INSTALLING PIP
            requirements_out = execute_cmd(cmd=commands["pip"], file_path=file_path)
            print requirements_out

        # ##########################################
        # MAKE SURE VIRTUAL ENVIRONMENT IS INSTALL
        # ##########################################
        env_version = int(str(env[0]).replace(".", "")) if len(env) > 0 else 0
        # print env_version
        if env_version > 1500:
            print "\t{:23}: {}".format("VIRTUALENV VERSION", env[0])
        else:
            # INSTALLING THE VIRTUAL ENV
            requirements_out = execute_cmd(cmd=commands["venv"], file_path=file_path)
            print requirements_out
    else:
        print "\n\t>>> PYTHON VERSION 2.7.12 IS REQUIRED TO RUN THE LENTICULAR LENS"
        exit(0)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # 2.3 CLONE OR PULTHE LENTICULAR LENS SOFTWARE
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    if os.path.isdir(join(directory, "alignments")) is False:
        print "\n{0}\n    >>> LENTICULAR LENS CLONE REQUEST\n{0}\n".format(highlight)
        cloning = commands["git_clone"].format(w_dir)
        execute_cmd(cloning, file_path, output=False, run=run)
    else:
        print "\n{0}\n    >>> LENTICULAR LENS PULL REQUEST\n{0}\n".format(highlight)
        pulling = commands["git_pull"].format(join(directory, "alignments"))
        execute_cmd(pulling, file_path, output=False, run=run)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # 2.4 UPDAT THE SEVER SETTINGS WITH STARDOG HOME AND BIN PATHS
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print "\n{0}\n    >>> UPDATING SERVER SETTINGS\n{0}\n".format(highlight)
    update_settings(directory, stardog_home, stardog_bin, database_name, ll_port)

    # 8. SLEEPING TIME FOR WINDOWS USER FOR CHECKING WHAT HAS BEE DONE SO FAR
    # AS A NEW WINDOW WILL PUP UP AND ERASE ALL PREVIUS OUPUTS
    if OPE_SYS == 'windows':

        class timeout(Cmd):
            def do_1(self, goon):
                return True

        command = timeout()
        command.prompt = '> '
        message = "\n{0}\n{1:^52}\n{2:^52}\n{0}\n".format(
            highlight, ">>>   I AM GOING TO SLEEP...", "PUNCH IN THE KEY [1] TO WAIKE ME UP")
        command.cmdloop(message)
        print "\n{1:^52}\n".format(highlight, "THANKS FOR WAIKING ME UP!")
        # print "\n{0}\n    >>> SLEEPING FOR 10 SECONDS FOR USER CHECKS\n{0}\n".format(highlight)
        # time.sleep(10)


# #####################################################
""" INSTALLATION: PLATFORM DEPENDENT """
# #####################################################


def win_install(directory, python_path, stardog_home, stardog_bin, run=False):

    # UPGRADE PIP
    # INSTALL THE VIRTUALENV AND ACTIVATE IT
    # INSTALL OR UPDATE THE REQUIREMENTS
    # RUN THE LENTICULAR LENS

    print "\n{0}\n    >>> WINDOWS INSTALLATIONS\n{0}\n".format(highlight)
    file_path = join(directory, "INSTALLATION.bat")
    w_dir = join(directory, "alignments")
    cmds = commands["windows"].format(w_dir, os.path.sep, python_path, stardog_bin, stardog_home)
    execute_cmd(cmds, file_path, output=False, run=run)
    wb.open_new_tab('http://localhost:5077/')


def mac_install(directory, python_path, stardog_home, stardog_bin, run=False):

    # UPGRADE PIP
    # INSTALL THE VIRTUALENV AND ACTIVATE IT
    # INSTALL OR UPDATE THE REQUIREMENTS
    # RUN THE LENTICULAR LENS

    print "\n{0}\n    >>> MAC/LINUX INSTALLATIONS\n{0}\n".format(highlight)
    file_path = join(directory, "INSTALLATION.sh")
    w_dir = join(directory, "alignments")
    cmds = commands["mac"].format(w_dir, os.path.sep, python_path, stardog_bin, stardog_home)
    execute_cmd(cmds, file_path, output=False, run=run)


# ######################################################
"""             INSTALLATION PARAMETERS              """
########################################################
# CHANGE THE FOLLOWING INFORMATIION
#   1. WORKING DIRECTORY PATH
#   2. PYTHON PATH
#   3. STADOG BIN DIRECTORY
#   4. STARDOG DATA BASE DIRECTORY
#   5. STARDOG BATABASE NAME
########################################################
#$######################################################

parameter_input = """

# ENTER FALSE IS YOU DO NOT NEED TO RUN THE TOOL
run = True

# PROVIDE THE FOLDER IN WHICH YOU WANT THE INSTALLATION FILES TO BE DOWNLOADED
directory = C:\Productivity\LinkAnalysis\Coverage\InstallTest\Install

# PROVIDE THE DIRECTORY OF YOUR PYTHON 2.7 FORLDER
python_path = C:\Python27

# PROVIDE THE STARDOG BIN PATH
stardog_bin = C:\Program Files\stardog-5.3.0\bin

# PROVIDE THE STARDOG HOME FOLDER
stardog_home = C:\Productivity\data\stardog

# THE DEFAULT DATABSED IS "risis"
database_name = risis

# 5077 IS THE DEFAULT PORT. NO NEED TO CHANGE UNLESS NEEDED.
ll_port = 5077

"""

# #####################################################
""" RUNNING THE LENTICULAR LENS INSTALLATION BASES
    ON THE PARAMETERS VALUES ENTERED ABOVE  """
# #####################################################

# install(parameter_input)

# #####################################################
""" RUNNING THE LENTICULAR LENS INSTALLATION BASES
    ON THE PARAMETERS VALUES ENTERED ABOVE
    MAC OR LINUX EXTRA OPTION USING ENV VARIABLES """
# #####################################################

# DIRECTORY="" PYTHON_PATH="" STARDOG_PATH="" STARDOG_DATA="" python LenticularLensInstallation.py


prompt = LLPrompt()
prompt.prompt = '> '
prompt.cmdloop(prompt.message)
