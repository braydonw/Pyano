
Needs 3 things:

- description of the project

- how users can install the project (add IO error checking so it wont fail if they dont have any IO connected - same for all library imports!!)

- how to basically use the project


Setup:

Clone/fork project
Create venv (link to tutorial)
Activate venv
Install requirements


# Pyano
> A Raspberry Pi powered self-playing piano using MIDI and python <br /> Created for Texas Tech University ECE - Project Lab II - Spring 2019

[![NPM Version][npm-image]][npm-url]
[![Build Status][travis-image]][travis-url]
[![Downloads Stats][npm-downloads]][npm-url]

One to two paragraph statement about your product and what it does.

![](header.png)


# Project Lab 2 - Spring 2019
### The Pyano Project: A Raspberry Pi Self-Playing Piano using MIDI and Python

## Need to add:
- Explain gui.ui and resources.qrc and how resources needs to be converted with (pyrcc4 -o resources....) and gui is converted at the top of gui.py file.
- Add how to change config file (shift on reboot to enter recovery mode) which is how you change resolution for 7 inch screen.

<br />


## Table of Contents
- [Virtual Environment & Package Setup](#1)
	- [ How to download ](#2)
	- [ How to run ](#3)


[Google Drive](https://drive.google.com/drive/folders/1dAa1gpMDAFGlhVw4SyiRp4k-08ug63ls) <br />
[GANTT Chart](https://docs.google.com/spreadsheets/d/1Dl2fH-6QJU7XaaoZwBGv_6Ten1BIh_QoUyknhaeHPaA/edit#gid=0) <br />
<br />

## Group Members
- Adan Chavez
- James Day
- Camilo Rincon
- Braydon Westmoreland

<br />

<a name="1"></a>
## Virtual Environment & Package Setup

<a name="2"></a>
### How to download the project from GitHub & setup a local virtual environment:

Make sure python3, pip, and git are all installed and up-to-date.

**(Step 1)** Clone this repository:

```
$ add updated link here (put /pyano-git at the end, but upload project to git as just pyano?)
```

**(Step 2)** Navigate to your local project folder:

```
$ cd /home/pi/pyano
```

**(Step 3)** Create your own virtual environment in the project folder and then activate it:

```
$ python3 -m venv venv
$ source env/bin/activate
```

Now you should have (venv) at the beginning of your terminal line.

**(Step 4)** Install necessary packages from requirements file:

```
$ pip install -r requirements.txt
```

**(Extra)** Update requirements after installing new packages to your local venv:

```
$ pip freeze > requirements.txt
```

<br />

<a name="3"></a>
### How to open & run python projects:
### THIS IS GOING TO CHANGE
To edit the main python project file:

```
$ nano pyano.py
```

To run the main python file:

```
$ python pyano.py
```

<br />

### How to upload the project to GitHub after modifying it:

**(Step 1)** See what files have been modified:

```
$ git status
```

**(Step 2)** Make a commit:

```
$ git commit -a
Enter your commit message, then ctrl+X, then Enter/Return.

$ git pull origin master
If everything is up-to-date press ctrl+X, then Enter/Return.

$ git push origin master
Enter your username and password.
```

Always make a pull before a push to ensure your local project has the most up-to-date git repo files. 

**(Step 3)** Remove the project directory from your device:

```
cd ..
This should put you in the directory containing the Pyano project folder.

rm -rf Pyano
```

For more git information such as branching and merging watch [this video](https://www.youtube.com/watch?v=HVsySz-h9r4&frags=pl%2Cwn). <br />
The latest Mido documentation can be found [here](https://mido.readthedocs.io/en/latest/). <br />
The latest Virtual Environment Wrapper documentation can be found [here](https://virtualenvwrapper.readthedocs.io/en/latest/#). <br />
<br />
Note that [Pipenv](https://pipenv.readthedocs.io/en/latest/) has become the new industry standard for working with python virtual environments. Fortunately, Pipenv was built with virtualenv backwards compatibility in mind. For a brief tutorial, watch [this video](https://www.youtube.com/watch?v=zDYL22QNiWk&t=246s).
<br />
<br />
<br /> 

## How to enable SSH on RPI for remote access
**(Step 1)** Open terminal on the Raspberry Pi and type:

```
$ ifconfig
```

**(Step 2)** Find the Pi's inet address (192.168.x.xxx) <br /> <br />
**(Step 3)** Then type this first line and follow the path below:

```
$ sudo raspi-config
5 - Interfacing Options
P2 - Enable SSH
Yes > Finish
```

[Video Reference](https://www.youtube.com/watch?v=IDqQIDL3LKg&index=3&list=PLQVvvaa0QuDesV8WWHLLXW_avmTzHmJLv)
<br /> 
<br /> 

## How to remote into RPI using SSH
Username: pi <br />
Default password: raspberry <br /> <br />
For Windows, you can download [Putty](https://www.putty.org/) or get the [Secure Shell App](https://chrome.google.com/webstore/detail/secure-shell-app/pnhechapfaindjhompbnflcldabbghjo?hl=en) for Google Chrome. <br /> 
For Mac, you can just open terminal and type:

```
$ ssh pi@192.168.x.xxx
```

You can then navigate to the project directory as if you were in the Pi. <br /> <br />
**(Important)** Don't forget to activate the virtual environment once you get into the Pi's terminal by navigating to the project directory and running the following:

```
$ source env/bin/activate
```

<br /> 


## PyQt4 & Qt Designer
Convert resources.qrc to resources.py

```
rcc4 -py3? resources.qrc -o resources.py

```

Convert layout.ui to layout.py

```
pyuic4 -py3? -x layout.ui -o layout.py -x 

```



<!-- Markdown link & img dfn's -->
[npm-image]: https://img.shields.io/npm/v/datadog-metrics.svg?style=flat-square
[npm-url]: https://npmjs.org/package/datadog-metrics
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
[wiki]: https://github.com/yourname/yourproject/wiki

