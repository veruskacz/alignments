
import os
import re
import sys
import time
import datetime
import platform
import fileinput
import subprocess
from os.path import join
import cStringIO as Buffer


# #####################################################
""" FUNCTION PARAMETERS """
# #####################################################

OPE_SYS = platform.system().lower()
_format = "%a %b %d %H:%M:%S %Y"
date = datetime.datetime.today()
begining = time.time()
_line = "------------------------------------------------------------------------------------------------------"
print "\n{}\n{:>90}\n{}\n".format(_line, date.strftime(_format), _line)


# #####################################################
""" FINSTALLATION FUNCTIONS """
# #####################################################

def normalise_path(file_path):

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

    wr = Buffer.StringIO()

    if os.path.isfile(file_path) is False:
        print "THE PROVIDED FILE BELOW DOES NOT EXIST" \
              "\n\t>>> {}\nFOR THAT YOUR ACTION HAS BEEN TERMINATED\n".format(file_path)
        exit(0)

    with open(name=file_path, mode="r") as reader:
        for line in reader:
            found = re.findall(search_exp, line)
            if len(found) > 0:
                print "\t{}".format(found[0])
                replaced = line.replace(found[0], replace_exp)
                wr.write(replaced)
            else:
                wr.write(line)

    with open(name=file_path, mode="w+") as writer:
        writer.write(wr.getvalue())


def update_settings(directory, stardog_home, stardog_bin, database_name):

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


def install(parameter_inputs):

    inputs_0 = re.findall("run[ ]*=[ ]*([^\"\'\n]+)", parameter_inputs)
    inputs_1 = re.findall("directory[ ]*=[ \"\']*([^\"\'\n]+)", parameter_inputs)
    inputs_2 = re.findall("python_path[ ]*=[ \"\']*([^\"\'\n]+)", parameter_inputs)
    inputs_3 = re.findall("stardog_bin[ ]*=[ \"\']*([^\"\'\n]*)", parameter_inputs)
    inputs_4 = re.findall("stardog_home[ ]*=[ \"\']*([^\"\'\n]*)", parameter_inputs)
    inputs_5 = re.findall("database_name[ ]*=[ \"\']*([^\"\'\n]*)", parameter_inputs)

    # DEFAULT_DATABASE = os.getenv("LL_STARDOG_DATABASE", "risis")

    run = bool(str(inputs_0[0]).strip()) if len(inputs_0) > 0 else None
    directory = normalise_path(str(inputs_1[0]).strip()) if len(inputs_1) > 0 else None
    python_path = normalise_path(str(inputs_2[0]).strip()) if len(inputs_2) > 0 else None
    stardog_bin = normalise_path(str(inputs_3[0]).strip()) if len(inputs_3) > 0 else None
    stardog_home = normalise_path(str(inputs_4[0]).strip()) if len(inputs_4) > 0 else None
    database_name = str(inputs_5[0]).strip() if len(inputs_5) > 0 else None

    print "{:23}: {}".format("INSTALLATION DIRECTORY", directory)
    print "{:23}: {}".format("INSTALLED PYTHON PATH", python_path)
    print "{:23}: {}".format("STARDOG DATA PATH", stardog_home)
    print "{:23}: {}".format("STARDOG HOME PATH", stardog_bin)
    print "{:23}: {}".format("DATABASE NAME", database_name)

    if run is None or directory is None or python_path is None or stardog_bin is None or \
                    stardog_home is None  or database_name is None:
        print "THERE IS A MISSING INPUT"
        return

    if OPE_SYS != "windows":
        if directory.__contains__("\\") or python_path.__contains__("\\") or stardog_bin.__contains__("\\") or \
                        stardog_home.__contains__("\\") is None:
            print "\nCHECK YOUR INPUT PATHS AGAIN AS IT LOOKS LIKE A WINDOWS PATH :-)\n"
            return

    directory = os.getenv("LL_DIRECTORY", directory)
    python_path = os.getenv("LL_PYTHON_PATH", python_path)
    stardog_bin = os.getenv("LL_STARDOG_PATH", stardog_bin)
    stardog_home = os.getenv("LL_STARDOG_DATA", stardog_home)
    database_name = os.getenv("LL_STARDOG_DATABASE", database_name)

    directory = directory.replace("\\", "\\\\")
    python_path = python_path.replace("\\", "\\\\")
    stardog_bin = stardog_bin.replace("\\", "\\\\")
    stardog_home = stardog_home.replace("\\", "\\\\")

    # RUNNING THE GENERIC INSTALLATION
    generic_install( directory, python_path, stardog_home,  stardog_bin,  database_name, run=run)

    # RUNNING WINDOWS SPECIFIC INSTALLATION
    if OPE_SYS == "windows":
        win_install(directory, python_path, stardog_home=stardog_home, stardog_bin=stardog_bin, run=run)

    # RUNNING MAC OR LINUX SPECIFIC INSTALLATION
    else:
        mac_install(directory, python_path, stardog_home=stardog_home, stardog_bin=stardog_bin, run=run)


def generic_install(directory, python_path, stardog_home, stardog_bin, database_name, run=False):

    print "{:23}: {}\n".format("COMPUTER TYPE", platform.system().upper())

    file_path = join(directory, "INSTALLATION.BAT" if OPE_SYS == "windows" else "INSTALLATION.sh")
    w_dir = join(directory, "alignments")
    requirements = """
        pip --version
        python --version
        virtualenv --version
        """

    # 1. CHECK WHETHER THE INSTALLATION DIRECTORY EXISTS
    if os.path.isdir(directory) is False:
        try:
            os.mkdir(directory)
            print "\nTHE PROVIDED DIRECTORY DID NOT EXIST BUT WAS CREATED\n"
        except:
            print "\nTHE PROVIDED DIRECTORY COULD NOT BE CREATED\n"
            return

    # 2. CREATE THE BATCH FILE FOR CHECKING PIP PYTHON AND VIRTUALENV
    with open(name=file_path, mode="wb") as writer:
        writer.write(requirements)

    # MAC PERMISSION ISSUES
    if OPE_SYS != 'windows':
        os.chmod(file_path, 0o777)

    requirements_output = subprocess.check_output(file_path, shell=True)
    requirements_output = str(requirements_output)

    # 3. PYTHON VERSION
    python = re.findall('python ([\d*\.]+)', str(requirements_output))
    python_version = int(str(python[0]).replace(".", "")) if len(python) > 0 else 0
    if (python_version >= 27) and (python_version < 2713):

        print "{:23}: {}".format("PYTHON VERSION", python[0])

        # MAKE SURE PIP IS INSTALL
        pip = re.findall('pip ([\d*\.]+)', str(requirements_output))
        pip_version = pip[0] if len(pip) > 0 else 0
        if pip_version > 0:
            print "{:23}: {}".format("PIP VERSION", pip_version)
        else:
            # BATCH FOR INSTALLING PIP
            with open(name=file_path, mode="wb") as writer:
                writer.write("call easy_install pip")
            # INSTALLING PIP
            requirements_output = subprocess.check_output(file_path, shell=True)
            print str(requirements_output)

        # VIRTUAL ENVIRONMENT
        env = re.findall('([\d*\.]+)\n', str(requirements_output))
        env_version = env[0] if len(env) > 0 else 0
        if env_version > 0:
            print "{:23}: {}".format("VIRTUALENV VERSION", env_version)
        else:
            # BATCH FOR INSTALLING THE VIRTUAL ENV
            with open(name=file_path, mode="wb") as writer:
                writer.write("call pip install virtualenv")
            # INSTALLING THE VIRTUAL ENV
            requirements_output = subprocess.check_output(file_path, shell=True)
            print str(requirements_output)
    else:
        print "PYTHON VERSION 2.7.12 IS REQUIRED TO RUN THE LENTICULAR LENS"
        exit(0)

    # 4. COMMAND FOR CLONING OR PULING THE LENTICULAR LENS SOFTWARE
    if os.path.isdir(join(directory, "alignments")) is False:
        print "------------------------------------------\n" \
              "    >>> LENTICULAR LENS CLONE REQUEST\n" \
              "------------------------------------------"
        cloning = """
        echo "CLONING THE LENTICULAR LENS SOFTWARE"
        git clone https://github.com/veruskacz/alignments.git {0}
        """.format(w_dir)
    else:
        print "---------------------------------------\n" \
              "    >>> LENTICULAR LENS PULL REQUEST\n" \
              "---------------------------------------"
        cloning = """
        cd {0}
        git pull
        """.format(join(directory, "alignments"))

    # 5. CREATING THE BATCH FILE
    with open(name=file_path, mode="wb") as writer:
        writer.write(cloning)

    # 6. EXECUTING THE BATCH FILE
    if run is True:
        subprocess.call(file_path, shell=True)

    # 7. UPDATING THE SEVER SETTINGS WITH STARDOG HOME AND BIN PATHS
    print "\n-------------------------------------\n" \
          "    >>> UPDATING SERVER SETTINGS\n" \
          "-------------------------------------\n"
    update_settings(directory, stardog_home, stardog_bin, database_name)

    # MAC PERMISSION ISSUES
    if OPE_SYS == 'windows':

        print "\n--------------------------------------------------\n" \
              "    >>> SLEETING FOR 20 SECONDS FOR USER CHECKS\n" \
              "----------------------------------------------------\n"

        time.sleep(20)


def win_install(directory, python_path, stardog_home, stardog_bin, run=False):

    # 8.
    # UPGRADE PIP
    # INSTALL THE VIRTUALENV AND ACTIVATE IT
    # INSTALL OR UPDATE THE REQUIREMENTS
    # RUN THE LENTICULAR LENS
    #

    print "\n-------------------------------------\n" \
          "    >>> WINDOWS INSTALLATIONS\n" \
          "-------------------------------------\n"

    file_path = join(directory, "INSTALLATION.sh")
    w_dir = join(directory, "alignments")
    os.chmod(file_path, 0o777)

    data = """
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
    echo "   >>> mac: LL_STARDOG_PATH="{3}" LL_STARDOG_DATA="{4}" python run.py"
    python run.py
    """.format(w_dir, os.path.sep, python_path, stardog_bin, stardog_home)

    with open(name=file_path, mode="wb") as writer:
        writer.write(data)

    if run is True:
        subprocess.call(file_path, shell=True)


def mac_install(directory, python_path, stardog_home, stardog_bin, run=False):

    print "-------------------------------------\n" \
          "    >>> MAC/LINUX INSTALLATIONS\n" \
          "-------------------------------------\n"

    # 8.
    # UPGRADE PIP
    # INSTALL THE VIRTUALENV AND ACTIVATE IT
    # INSTALL OR UPDATE THE REQUIREMENTS
    # RUN THE LENTICULAR LENS
    # {1}python.exe
    file_path = join(directory, "INSTALLATION.BAT")
    w_dir = join(directory, "alignments")
    data = """

    echo "    >>> UPGRADING PIP"
    sudo python -m pip install --upgrade pip

    echo "    >>> CLONING THE LENTICULAR LENS SOFTWARE"
    echo git clone https://github.com/veruskacz/alignments.git {0}

    echo "    >>> CREATING A VIRTUAL ENVIRONMENT"
    virtualenv  --python={2} {0}

    echo "    >>> ACTIVATING THE VIRTUAL ENVIRONMENT"
    source {0}{1}bin/activate

    echo "    >>> INSTALLING THE LENTICULAR LENS REQUIREMENTS"
    sudo pip install -r  {0}{1}requirements.txt

    echo "    >>> INSTALLATION DONE..."
    echo "    >>> RUNNING THE LENTICULAR LENS"
    cd {0}{1}src
    LL_STARDOG_PATH="{3}" LL_STARDOG_DATA="{4}" python run.py
    """.format(w_dir, os.path.sep, python_path, stardog_bin, stardog_home)

    with open(name=file_path, mode="wb") as writer:
        writer.write(data)

    if run is True:
        subprocess.call(file_path, shell=True)
        # output = subprocess.check_output(file_path, shell=True)
        # output = re.sub(' .*>', ' ', output)
        # print output


# def win_installs(directory, python_path, stardog_home, stardog_bin, database_name, run=False):
#
#     print "{:23}: {}".format("COMPUTER TYPE", platform.system().upper())
#
#     file_path = join(directory, "INSTALLATION.BAT")
#     w_dir = join(directory, "alignments")
#     requirements = """
#     call pip --version
#     call python --version
#     call virtualenv --version
#     """
#
#     # 1. CHECK WHETHER THE INSTALLATION DIRECTORY EXISTS
#     if os.path.isdir(directory) is False:
#         try:
#             os.mkdir(directory)
#             print "\nTHE PROVIDED DIRECTORY DID NOT EXIST BUT WAS CREATED\n"
#         except:
#             print "\nTHE PROVIDED DIRECTORY COULD NOT BE CREATED\n"
#             return
#
#     # 2. CREATE THE BATCH FILE FOR CHECKING PIP PYTHON AND VIRTUALENV
#     with open(name=file_path, mode="wb") as writer:
#         writer.write(requirements)
#     requirements_output = subprocess.check_output(file_path, shell=True)
#     requirements_output = str(requirements_output)
#
#     # 3. PYTHON VERSION
#     python = re.findall('python ([\d*\.]+)', str(requirements_output))
#     python_version = int(str(python[0]).replace(".", "")) if len(python) > 0 else 0
#     if (python_version >= 27) and (python_version < 2713):
#
#         print "{:23}: {}".format("PYTHON VERSION", python[0])
#
#         # MAKE SURE PIP IS INSTALL
#         pip = re.findall('pip ([\d*\.]+)', str(requirements_output))
#         pip_version = pip[0] if len(pip) > 0 else 0
#         if pip_version > 0:
#             print "{:23}: {}".format("PIP VERSION", pip_version)
#         else:
#             # BATCH FOR INSTALLING PIP
#             with open(name=file_path, mode="wb") as writer:
#                 writer.write("call easy_install pip")
#             # INSTALLING PIP
#             requirements_output = subprocess.check_output(file_path, shell=True)
#             print str(requirements_output)
#
#         # VIRTUAL ENVIRONMENT
#         env = re.findall('([\d*\.]+)\n', str(requirements_output))
#         env_version = env[0] if len(env) > 0 else 0
#         if env_version > 0:
#             print "{:23}: {}".format("VIRTUALENV VERSION", env_version)
#         else:
#             # BATCH FOR INSTALLING THE VIRTUAL ENV
#             with open(name=file_path, mode="wb") as writer:
#                 writer.write("call pip install virtualenv")
#             # INSTALLING THE VIRTUAL ENV
#             requirements_output = subprocess.check_output(file_path, shell=True)
#             print str(requirements_output)
#     else:
#         print "PYTHON VERSION 2.7.12 IS REQUIRED TO RUN THE LENTICULAR LENS"
#         exit(0)
#
#     # 4. COMMAND FOR CLONING OR PULING THE LENTICULAR LENS SOFTWARE
#     if os.path.isdir(join(directory, "alignments")) is False:
#         print "----------------------------------------\n" \
#               " >>> LENTICULAR LENS CLONE REQUEST\n" \
#               "---------------------------------------"
#         cloning = """
#     echo "CLONING THE LENTICULAR LENS SOFTWARE"
#     git clone https://github.com/veruskacz/alignments.git {0}
#     """.format(w_dir)
#     else:
#         print "-----------------------------------\n" \
#               ">>> LENTICULAR LENS PULL REQUEST\n" \
#               "-----------------------------------"
#         cloning = """
#     cd {0}
#     git pull
#     """.format(join(directory, "alignments"))
#
#     # 5. CREATING THE BATCH FILE
#     with open(name=file_path, mode="wb") as writer:
#         writer.write(cloning)
#
#     # 6. EXECUTING THE BATCH FILE
#     if run is True:
#         subprocess.call(file_path, shell=True)
#     exit(0)
#     # 7. UPDATING THE SEVER SETTINGS WITH STARDOG HOME AND BIN PATHS
#     update_settings(directory, stardog_home, stardog_bin, database_name)
#
#     # 8.
#     # UPGRADE PIP
#     # INSTALL THE VIRTUALENV AND ACTIVATE IT
#     # INSTALL OR UPDATE THE REQUIREMENTS
#     # RUN THE LENTICULAR LENS
#     # {1}python.exe
#
#     data = """
#     cls
#     echo "UPGRADING PIP"
#     python -m pip install --upgrade pip
#
#     echo "CLONING THE LENTICULAR LENS SOFTWARE"
#     echo git clone https://github.com/alkoudouss/alignments.git {0}
#
#     echo "CREATING A VIRTUAL ENVIRONMENT"
#     virtualenv  --python={2} {0}
#
#     echo "ACTIVATING THE VIRTUAL ENVIRONMENT"
#     call {0}{1}Scripts{1}activate.bat
#
#     echo "INSTALLING THE LENTICULAR LENS REQUIREMENTS"
#     pip install -r  {0}{1}requirements.txt
#
#     echo "INSTALLATION DONE..."
#     echo "RUNNING THE LENTICULAR LENS"
#     cd {0}{1}src
#     echo mac: LL_STARDOG_PATH="{3}" LL_STARDOG_DATA="{4}" python run.py
#     python run.py
#     """.format(w_dir, os.path.sep, python_path, stardog_bin, stardog_home)
#
#     with open(name=file_path, mode="wb") as writer:
#         writer.write(data)
#
#     if run is True:
#         subprocess.call(file_path, shell=True)
#         # output = subprocess.check_output(file_path, shell=True)
#         # output = re.sub(' .*>', ' ', output)
#         # print output
#
#
# def mac_installs(directory, python_path, stardog_home, stardog_bin, database_name, run=False):
#
#     print "{:23}: {}".format("COMPUTER TYPE", platform.system().upper())
#
#     if directory.__contains__("\\") or python_path.__contains__("\\") or stardog_bin.__contains__("\\") or \
#                     stardog_home.__contains__("\\") is None:
#         print "CHECK YOUR INPUT PATHS AGAIN AS IT LOOKS LIKE A WINDOWS PATH :-)"
#         return
#
#     file_path = join(directory, "INSTALLATION.sh")
#     w_dir = join(directory, "alignments")
#     requirements = """
#     pip --version
#     python --version
#     virtualenv --version
#     """
#
#     # 1. CHECK WHETHER THE INSTALLATION DIRECTORY EXISTS
#     if os.path.isdir(directory) is False:
#         try:
#             os.mkdir(directory)
#             print "\nTHE PROVIDED DIRECTORY DID NOT EXIST BUT WAS CREATED\n"
#         except :
#             print "\nTHE PROVIDED DIRECTORY COULD NOT BE CREATED\n"
#             return
#
#     # 2. CREATE THE BATCH FILE FOR CHECKING PIP PYTHON AND VIRTUALENV
#     with open(name=file_path, mode="wb") as writer:
#         writer.write(requirements)
#     if OPE_SYS != 'windows':
#         os.chmod(file_path, 0o777)
#
#     requirements_output = subprocess.check_output(file_path, shell=True)
#     requirements_output = str(requirements_output)
#
#     # 3. PYTHON VERSION
#     python = re.findall('python ([\d*\.]+)', str(requirements_output))
#     python_version = int(str(python[0]).replace(".", "")) if len(python) > 0 else 0
#     if (python_version >= 27) and (python_version < 2713):
#
#         print "{:23}: {}".format("PYTHON VERSION", python[0])
#
#         # MAKE SURE PIP IS INSTALL
#         pip = re.findall('pip ([\d*\.]+)', str(requirements_output))
#         pip_version = pip[0] if len(pip) > 0 else 0
#         if pip_version > 0:
#             print "{:23}: {}".format("PIP VERSION", pip_version)
#         else:
#             # BATCH FOR INSTALLING PIP
#             with open(name=file_path, mode="wb") as writer:
#                 writer.write("call easy_install pip")
#             # INSTALLING PIP
#             requirements_output = subprocess.check_output(file_path, shell=True)
#             print str(requirements_output)
#
#         # VIRTUAL ENVIRONMENT
#         env = re.findall('([\d*\.]+)\n', str(requirements_output))
#         env_version = env[0] if len(env) > 0 else 0
#         if env_version > 0:
#             print "{:23}: {}".format("VIRTUALENV VERSION", env_version)
#         else:
#             # BATCH FOR INSTALLING THE VIRTUAL ENV
#             with open(name=file_path, mode="wb") as writer:
#                 writer.write("call pip install virtualenv")
#             # INSTALLING THE VIRTUAL ENV
#             requirements_output = subprocess.check_output(file_path, shell=True)
#             print str(requirements_output)
#     else:
#         print "PYTHON VERSION 2.7.12 IS REQUIRED TO RUN THE LENTICULAR LENS"
#         exit(0)
#
#     # 4. COMMAND FOR CLONING OR PULING THE LENTICULAR LENS SOFTWARE
#     cloning = """
#     echo "CLONING THE LENTICULAR LENS SOFTWARE"
#     git clone https://github.com/veruskacz/alignments.git {0}
#     """.format(w_dir)
#
#     # 5. CREATING THE BATCH FILE
#     with open(name=file_path, mode="wb") as writer:
#         writer.write(cloning)
#
#     # 6. EXECUTING THE BATCH FILE
#     if run is True:
#         subprocess.call(file_path, shell=True)
#
#     # 7. UPDATING THE SEVER SETTINGS WITH STARDOG HOME AND BIN PATHS
#     update_settings(directory, stardog_home, stardog_bin, database_name)
#
#     # 8.
#     # UPGRADE PIP
#     # INSTALL THE VIRTUALENV AND ACTIVATE IT
#     # INSTALL OR UPDATE THE REQUIREMENTS
#     # RUN THE LENTICULAR LENS
#     # {1}python.exe
#     data = """
#
#     echo "UPGRADING PIP"
#     sudo python -m pip install --upgrade pip
#
#     echo "CLONING THE LENTICULAR LENS SOFTWARE"
#     echo git clone https://github.com/veruskacz/alignments.git {0}
#
#     echo "CREATING A VIRTUAL ENVIRONMENT"
#     virtualenv  --python={2} {0}
#
#     echo "ACTIVATING THE VIRTUAL ENVIRONMENT"
#     source {0}{1}bin/activate
#
#     echo "INSTALLING THE LENTICULAR LENS REQUIREMENTS"
#     sudo pip install -r  {0}{1}requirements.txt
#
#     echo "INSTALLATION DONE..."
#     echo "RUNNING THE LENTICULAR LENS"
#     cd {0}{1}src
#     LL_STARDOG_PATH="{3}" LL_STARDOG_DATA="{4}" python run.py
#     """.format(w_dir, os.path.sep, python_path, stardog_bin, stardog_home)
#
#     with open(name=file_path, mode="wb") as writer:
#         writer.write(data)
#
#     if run is True:
#         subprocess.call(file_path, shell=True)
#         # output = subprocess.check_output(file_path, shell=True)
#         # output = re.sub(' .*>', ' ', output)
#         # print output


################################################################################################
# CHANGE THE WORKING DIRECTORY, PYTHON PATH A
################################################################################################

# directory = "C:\Productivity\LinkAnalysis\Coverage\InstallTest"
# python_path = "C:\Python27"
# stardog_bin = 'C:\Program Files\stardog-5.3.0\\bin'
# stardog_home = "C:\Productivity\data\stardog"

# #####################################################
""" INSTALLATION PARAMETERS """
# #####################################################

parameter_input = """

run = True
directory = C:\Productivity\LinkAnalysis\Coverage\InstallTest\Install
python_path = C:\Python27
stardog_bin = C:\Program Files\stardog-5.3.0\bin
stardog_home = C:\Productivity\data\stardog
database_name = risis
"""


# #####################################################
""" RUNNING THE LENTICULAR LENS INSTALLATION BASES
    ON THE PARAMETERS VALUES ENTERED ABOVE  """
# #####################################################

install(parameter_input)


# #####################################################
""" RUNNING THE LENTICULAR LENS INSTALLATION BASES
    ON THE PARAMETERS VALUES ENTERED ABOVE
    MAC OR LINUX EXTRA OPTION USING ENV VARIABLES """
# #####################################################

# DIRECTORY="" PYTHON_PATH="" STARDOG_PATH="" STARDOG_DATA="" python LenticularLensInstallation.py
