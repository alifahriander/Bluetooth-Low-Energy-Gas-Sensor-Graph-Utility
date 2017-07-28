Bluetooth-Low-Energy-Gas-Sensor-Graph-Utility
==============================

Display data from a CMUT gas sensor using Bluetooth LE

Written by: Derek Santos
------------------------

Requirements
------------
* Python 3.x
* PyQt5
* PyQtGraph
* pysftp
* Known to run on Windows and Linux

How to install
--------------

#### Windows and OSX:
The following are the commands used with pip3 installed.

> pip3 install pyqtgraph

> pip3 install pyqt5

Next if you have git install in your computer you can run:
> git clone https://github.com/santosderek/Bluetooth-Low-Energy-Gas-Sensor-Graph-Utility

...or click the "Download" button on the github page.

Lastly, configure the config.py as intended, and run the following command within the graph_client directory:
> python3 main.py

*** If on OSX you might need to use 'sudo' before the command. ***

#### Linux:
The following commands are within linux_install.sh.

You can run:
> bash linux_install.sh

Or can install using the following commands in order:
> sudo apt-get -y update

> sudo apt-get -y upgrade

> sudo apt-get install -y python3=3.5.1-3

> sudo apt-get install -y python3-pyqt5

> sudo apt-get install -y python3-pip

> sudo pip3 install pysftp

> sudo pip3 install pyqtgraph

> sudo apt-get install -y git

Next if you have git install in your computer you can run:
> git clone https://github.com/santosderek/Bluetooth-Low-Energy-Gas-Sensor-Graph-Utility

...or click the "Download" button on the github page.

Lastly, configure the config.py as intended, and run the following command within the graph_client directory:
> python3 main.py

*** You might need to use 'sudo' before the command. ***

*** If you experience troubles installing on ARM architecture you may need: ***

> sudo apt-get install libffi-dev

> sudo apt-get install libssl-dev

> sudo apt-get install python-dev

> sudo apt-get install python3-dev


#### Optional


The setup.py is only after you have installed the dependencies.

This will allow you to run the command 'graphclient' to run the script from any directory.
