
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


OPE_SYS = platform.system().lower()
_format = "%a %b %d %H:%M:%S %Y"
date = datetime.datetime.today()
begining = time.time()
_line = "------------------------------------------------------------------------------------------------------"
print "\n{}\n{:>90}\n{}\n".format(_line, date.strftime(_format), _line)





def replaceAll(file, searchExp, replaceExp):

    wr = Buffer.StringIO()

    if os.path.isfile(file) is False:
        print "THE PROVIDED FILE BELOW DOES NOT EXIST\n\t>>> {}\nFOR THAT YOUR ACTION HAS BEEN TERMINATED".format(file)
        exit(0)

    # print file

    with open(name=file, mode="r") as reader:
        for line in reader:
            found = re.findall(searchExp, line)
            if  len(found) > 0:
                print found
                replaced = line.replace(found[0], replaceExp)
                wr.write(replaced)
            else:
                wr.write(line)

    # print wr.getvalue()
    # text = reader.readlines()
    # print text
    #
    with open(name=file, mode="w+") as writer:
        writer.write(wr.getvalue())


    # for line in fileinput.input(file, inplace=1):
    #     print file
    #     print line
        # if searchExp in line:
        #     line = line.replace(searchExp, replaceExp)
        # sys.stdout.write(line)


def update_settings(directory, stardog_home, stardog_bin):

    svr_settings = join(directory, "alignments{0}src{0}Alignments{0}Server_Settings.py".format(os.path.sep))

    # STARDOG BIN
    s_bin = """\"LL_STARDOG_PATH", "(.*)\""""
    replaceAll(svr_settings, s_bin, """LL_STARDOG_PATH = {0}{1}{1}""".format(stardog_bin, os.path.sep))

    # STARDOG DATA OF HOME
    s_data = """"LL_STARDOG_DATA", "(.*)\""""
    replaceAll(svr_settings, s_data, """LL_STARDOG_DATA = {}""".format(stardog_home))


def install(directory, python_path, stardog_home, stardog_bin, run=False):

    directory = os.getenv("LL_DIRECTORY", directory)
    python_path = os.getenv("LL_PYTHON_PATH", python_path)
    stardog_bin = os.getenv("LL_STARDOG_PATH", stardog_bin)
    stardog_home = os.getenv("LL_STARDOG_DATA", stardog_home)

    if OPE_SYS == "windows":
        win_install(directory, python_path, stardog_home=stardog_home, stardog_bin=stardog_bin, run=run)

    else:
        mac_install(directory, python_path, stardog_home=stardog_home, stardog_bin=stardog_bin, run=run)


def win_install(directory, python_path, stardog_home, stardog_bin, run=False):

    print "{:23}: {}".format("INSTALLATION DIRECTORY", directory)
    print "{:23}: {}".format("INSTALLED PYTHON PATH", python_path)

    file_path = join(directory, "INSTALLATION.BAT")
    w_dir = join(directory, "alignments")
    requirements = """
    call pip --version
    call python --version
    call virtualenv --version
    """

    if os.path.isfile(file_path) is False:
        print "THE PROVIDED FILE BELOW DOES NOT EXIST\n\t>>> {}\nFOR THAT YOUR ACTION HAS BEEN TERMINATED".format(file)
        exit(0)

    with open(name=file_path, mode="wb") as writer:
        writer.write(requirements)
    requirements_output = subprocess.check_output(file_path, shell=True)
    requirements_output = str(requirements_output)

    # PYTHON VERSION
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

    # UPGRADE PIP - CLONE THE LENTICULAR LENS - INSTALL THE VIRTUALENV AND ACTIVATE IT
    # {1}python.exe


    cloning = """
    echo "CLONING THE LENTICULAR LENS SOFTWARE"
    git clone https://github.com/veruskacz/alignments.git {0}
    """.format(w_dir)

    with open(name=file_path, mode="wb") as writer:
        writer.write(cloning)

    if run is True:
        subprocess.call(file_path, shell=True)

    update_settings(directory, stardog_home, stardog_bin)

    #
    data = """

    echo "UPGRADING PIP"
    python -m pip install --upgrade pip

    echo "CLONING THE LENTICULAR LENS SOFTWARE"
    echo git clone https://github.com/alkoudouss/alignments.git {0}

    echo "CREATING A VIRTUAL ENVIRONMENT"
    virtualenv  --python={2} {0}

    echo "ACTIVATING THE VIRTUAL ENVIRONMENT"
    call {0}{1}Scripts{1}activate.bat

    echo "INSTALLING THE LENTICULAR LENS REQUIREMENTS"
    pip install -r  {0}{1}requirements.txt

    echo "INSTALLATION DONE..."
    echo "RUNNING THE LENTICULAR LENS"
    cd {0}{1}src
    echo mac: LL_STARDOG_PATH="{3}" LL_STARDOG_DATA="{4}" python run.py
    python run.py
    """.format(w_dir, os.path.sep, python_path, stardog_bin, stardog_home)

    with open(name=file_path, mode="wb") as writer:
        writer.write(data)

    if run is True:
        subprocess.call(file_path, shell=True)
        # output = subprocess.check_output(file_path, shell=True)
        # output = re.sub(' .*>', ' ', output)
        # print output


def mac_install(directory, python_path, stardog_home, stardog_bin, run=False):

    print "We are mac"
    print "{:23}: {}".format("INSTALLATION DIRECTORY", directory)
    print "{:23}: {}".format("INSTALLED PYTHOM PATH", python_path)

    file_path = join(directory, "INSTALLATION.sh")
    w_dir = join(directory, "alignments")
    requirements = """
    pip --version
    python --version
    virtualenv --version
    """

    if os.path.isfile(file_path) is False:
        print "THE PROVIDED FILE BELOW DOES NOT EXIST\n\t>>> {}\nFOR THAT YOUR ACTION HAS BEEN TERMINATED".format(file)
        exit(0)

    with open(name=file_path, mode="wb") as writer:
        writer.write(requirements)
    if OPE_SYS != 'windows':
        os.chmod(file_path, 0o777)
        # print "MAC"
    requirements_output = subprocess.check_output(file_path, shell=True)
    requirements_output = str(requirements_output)
    # print requirements_output
    # os.system("{}".format(file_path))

    # PYTHON VERSION
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


    # UPGRADE PIP - CLONE THE LENTICULAR LENS - INSTALL THE VIRTUALENV AND ACTIVATE IT
    # {1}python.exe
    data = """

    echo "UPGRADING PIP"
    sudo python -m pip install --upgrade pip

    echo "CLONING THE LENTICULAR LENS SOFTWARE"
    git clone https://github.com/alkoudouss/alignments.git {0}

    echo "CREATING A VIRTUAL ENVIRONMENT"
    virtualenv  --python={2} {0}

    echo "ACTIVATING THE VIRTUAL ENVIRONMENT"
    source {0}{1}bin/activate

    echo "INSTALLING THE LENTICULAR LENS REQUIREMENTS"
    sudo pip install -r  {0}{1}requirements.txt

    echo "INSTALLATION DONE..."
    echo "RUNNING THE LENTICULAR LENS"
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


################################################################################################
# CHANGE THE WORKING DIRECTORY, PYTHON PATH A
################################################################################################

directory="C:\Productivity\LinkAnalysis\Coverage\InstallTest"
python_path="C:\Python27"
stardog_bin='C:\Program Files\stardog-5.3.0\\bin'
stardog_home="C:\Productivity\data\stardog"

install(directory, python_path, stardog_home, stardog_bin, run=True)

## sudo
## DIRECTORY="" PYTHON_PATH="" STARDOG_PATH="" STARDOG_DATA="" python LenticularLensInstallation.py
