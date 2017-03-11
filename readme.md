# Alignment & Specs Demo

This web application can show off the coolness of the Sngleton*** model developed by Al Idrissou

## Setup

* Make sure you have `pip` and `virtualenv` installed (`easy_install pip`, `pip install virtualenv`)
* Go to the directory in which you cloned this Git repository, and install a virtual environment: `virtualenv .`
* Activate the virtual environment: `source bin/activate` (linux-based) | Scripts\activate.bat (windows)
* Install the required packages: `pip install -r requirements.txt`
* Make sure you have a properly installed Stardog server running, with **security disabled** (`stardog-admin server start --disable-security`)
  * Expected database address/name: http://localhost:5820/risis
* Inside the `src` directory, run `python run.py`
* Go to `http://localhost:5000` and have fun!
