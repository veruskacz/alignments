

# Alignment & Specs Demo

This web application can show off the coolness of the Sngleton*** model developed by Al Idrissou

## Setup

1. Make sure you have `pip` and `virtualenv` installed 
	[easy_install pip]
	[pip install virtualenv]
	
2. Create a directory where you want to download the software.

3. Go to the directory and clone it from git: git clone https://github.com/alkoudouss/alignmnents
	
4. Go to the directory in which you cloned this Git repository, and install a virtual environment: 
	[virtualenv .]
	
5. Activate the virtual environment: 
	[source bin/activate]	(linux-based)
	[Scripts\activate.bat]	(windows)
	
6. Install the required packages: 
	[pip install -r requirements.txt]
	
7. Make sure you have a properly installed Stardog server running, with **security disabled** 
	[stardog-admin server start --disable-security]

8. Create the database 'risis' from command line as
	stardog-admin db create -o spatial.enabled=true search.enabled=true strict.parsing=false -n risis
	
9. Expected database address/name: http://localhost:5820/risis

10. Edit this file \src\Alignments\Server_Settings.py depending on whether you are a WINDOWs, MAC OR LINUX user

	* EXAMPLE 1
	```
	SERVER_MAC = "localhost:5820"
	STARDOG_PATH_MAC = '/Applications/stardog-5.0.2/bin/'
	STARDOG_DATA_PATH_MAC = "/Users/userX/data/"
	```
	
	* EXAMPLE 2
	```
	SERVER_LINUX = "stardog.server.d2s.labs.vu.nl"	
	STARDOG_PATH_LINUX = '/scratch/risis/data/stardog/stardog-5.0/stardog-5.0/bin/'	
	STARDOG_DATA_PATH_LINUX = '/scratch/risis/data/stardog/stardog-5.0/stardog-5.0/data/'
	```
	
	* EXAMPLE 3 IS CURRENTLY ACTIVATED
	```
	SERVER_WIN = "localhost:5820"	
	STARDOG_PATH_WIN= 'C:\\Program Files\\stardog-5.0.5.1\\bin\\'	
	STARDOG_DATA_PATH_WIN = "C:\\Productivity\\data\\stardog"
	```
	
11. In the same file, depending on your choice above, uncomment the right option and comment the current option whenever necessary
	
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
	
12. Inside the `src` directory, run `python run.py`

13. Go to `http://localhost:5077` and have fun!
