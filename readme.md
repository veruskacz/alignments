
# Alignment & Specs Demo

This web application can show off the coolness of the Lenticular Lenses software with Singleton*** model developed by Al Idrissou
The installation of the software can be done using either of the following options further detailed in this "read me".

*  **All-in-one installation code**
* **Step-by-step on the command line**

## Required Software
1. Make sure you have `git` installed [https://git-scm.com/downloads]
2. Make sure you have  `python 2.7` installed [follow this link to install python 2.7 according to your operating system: http://docs.python-guide.org/en/latest/starting/installation/]
 3. Make sure you have a `Stardog` properly installed (see instructions in https://github.com/RinkeHoekstra/semanticweb-web-application-tutorial/blob/master/tools.md)

## All-in-One Installation Code Setup
1. Save the [LenticularLensInstallation.py](https://raw.githubusercontent.com/alkoudouss/alignments/master/LenticularLensInstallation.py) python code in an `installation-folder` of your choice  `(for example C:\LenticularLens\LenticularLensInstallation.py)` by first clicking on the above link, then right clicking on the web page and finally choosing the `save-as` option.
2. Open the `LenticularLensInstallation.py`, scroll down to the end of the file and edit the `parameter_input` with the right paths.
directory				: is the installation folder.
python_path		: is the folder where python  is installed.
stardog_bin		: is stardog bin path
stardog_home    : is stardog data folder
database_name	: is the stardog database name you will work on.

	```
	WINDOWS EXAMPLE
		parameter_input = """
		run = True
		directory = C:\LenticularLens
		python_path = C:\Python27
		stardog_bin = C:\Program Files\stardog-5.3.0\bin
		stardog_home = C:\data\stardog
		database_name = risis
		"""
	```
	```
	BIG-MAC EXAMPLE
		parameter_input = """
		run = True
		directory = /Users/USERNAME/LenticularLens
		python_path = /usr/bin/python2.7
		stardog_bin = /Applications/stardog-5.2.0/bin/
		stardog_home = /Users/USERNAME/data/stardog/
		database_name = risis
		"""
	```
3. Open the command line:
	##### WINDOWS :	Press the `windows button` and the `R button` pitch in `cmd` and `enter`
	##### BIG-MAC:  Press the `command button` and the `space button` pitch in `terminal` and `enter`

4. Go to the installation folder where `LenticularLensInstallation.py` is copied:
	```
	cd path-to-installation-folder
	example: cd C:\LenticularLens
	```

5. Run the code:
```python LenticularLensInstallation.py```

6. #### Go to `http://localhost:5820` and have fun with Stardog!
7. #### Go to `http://localhost:5077` and have fun with the Lenticular Lens!

## Step-by-Step Setup

1. Make sure you have   `pip` and `virtualenv` installed (only once)
   ```easy_install pip```
   ```pip install virtualenv```

2. Install the Lenticular Lenses software  (only once)
   2.1 Create a directory where you want to install the software
   2.2 Download the software from github.com, choose one of the options
   * If you have a git installed and a github account:
      * in the terminal, go to the directory created above
      * ```git clone https://github.com/alkoudouss/alignmnents.git```
   * Otherwise:
      * go to https://github.com/alkoudouss/alignmnents
      * click on `clone or download` and choose the option `download zip`.
      * copy the zip file to the directory created above
      * unzip the file

3. Setting up the Lenticular Lenses software and its requirements (only once)
   3.1. Adjusting system settings: edit this file `\src\Alignments\Server_Settings.py` depending on whether you are a WINDOWs, MAC OR LINUX user

   * EXAMPLE MAC SETTINGS
   ```
   SERVER_MAC = "localhost:5820"
   STARDOG_PATH_MAC = '/Applications/stardog-5.0.2/bin/'
   STARDOG_DATA_PATH_MAC = "/Users/userX/data/"
   ```

   * EXAMPLE LINUX SETTINGS
   ```
   SERVER_LINUX = "stardog.server.d2s.labs.vu.nl"
   STARDOG_PATH_LINUX = '/scratch/risis/data/stardog/stardog-5.0/stardog-5.0/bin/'
   STARDOG_DATA_PATH_LINUX = '/scratch/risis/data/stardog/stardog-5.0/stardog-5.0/data/'
   ```

   * EXAMPLE WINDOWNS SETTINGS (IS CURRENTLY ACTIVATED)
   ```
   SERVER_WIN = "localhost:5820"
   STARDOG_PATH_WIN= 'C:\\Program Files\\stardog-5.0.5.1\\bin\\'
   STARDOG_DATA_PATH_WIN = "C:\\Productivity\\data\\stardog"
   ```

   In the same file, depending on your choice above, uncomment the right option and comment the current option if necessary

   ```
   # STARDOG SERVER LOCAL HOST NAME
    # St.stardog_host_name: SERVER_LINUX,
    # St.stardog_host_name: SERVER_MAC,
    St.stardog_host_name: SERVER_WIN,
   ```

   ```
    # STARDOG PATH
    # St.stardog_path: STARDOG_PATH_LINUX,
    # St.stardog_path: STARDOG_PATH_MAC,
    St.stardog_path: STARDOG_PATH_WIN,
   ```

   ```
    # STARDOG DATA PATH
    # St.stardog_data_path: STARDOG_DATA_PATH_LINUX,
    # St.stardog_data_path: STARDOG_DATA_PATH_MAC,
    St.stardog_data_path: STARDOG_DATA_PATH_WIN,
       ```

   3.2. Installing Python Package Requirements with Virtual Environment:

   3.2.1. Virtual Environment Installation:
   * Go to the directory in which you cloned this Git repository, and install a virtual environment running one of the commands:
   `virtualenv .` if you have only python 2.7 installed
   `virtualenv --python=/usr/bin/python2.7 .` if you have several python versions installed

   3.2.2. Virtual Environment Activation:
   * Go to the directory in which you cloned this Git repository, and install a virtual environment running one of the commands:
   `source bin/activate`  (linux-based)
   `Scripts\activate.bat` (windows)

   3.2.3. Install the required packages:
   * Go to the directory cloned from git repository, where the file `requirements.txt` is and run the command:
   `pip install -r requirements.txt`

4. Setting up and running Stardog triple store (only once):
   4.1. Make sure you have Stardog server running with **security disabled**
   `stardog-admin server start --disable-security`
   4.2. Create the database 'risis' from command line as
   ```stardog-admin db create -o spatial.enabled=true search.enabled=true strict.parsing=false -n risis```
   4.3. You can check it on: `http://localhost:5820/risis`

5. Running the Lenticular Lenses software:
   5.1. If you have just followed the steps above:
   * Inside the `src` directory, run `python run.py`
   5.2. If you have restarted your computer, you will need to re-run some steps before the one above: `steps 3.2.2 and 4.1`

   5.2. If you have restarted only you terminal, you will need to re-run some steps: `step 3.2.2`

6. #### Go to `http://localhost:5820` and have fun with Stardog!
7. #### Go to `http://localhost:5077` and have fun with the Lenticular Lens!