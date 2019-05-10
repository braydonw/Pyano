# The Pyano Project

The Pyano is a 25-key self-playing piano powered by a Raspberry Pi using python and the MIDI file format. There are currently four modes of operation. The *player* mode is used to playback MIDI files on the miniature piano using a series of push-pull solenoids. The *maker* mode is used to create custom MIDI files with a standard qwerty keyboard. The *live* mode removes the need for MIDI files altogether and allows for a direct connection between qwerty keyboard inputs and solenoid activations on the piano. The *hero* mode is a work-in-progress addition that attempts to replicate guitar hero but with a piano. 

> Created for: <br />
> Texas Tech University <br />
> Dept. of Electrical & Computer Engineering <br />
> Project Lab II <br />
> Spring 2019 <br />

<br />

![Pyano GUI Main Menu](docs/gui-tour.gif?raw=true "Pyano GUI Main Menu")

<br />

[Click here for a short video demonstration](https://youtu.be/wNDljW7Iz3w)

<br />

## Table of Contents
- [Built With](#1)
- [Getting Started](#2)
- [Contributing](#3)
- [Project Team](#4)
- [GANNT Chart](#5)
- [License](#6)

<br />

<a name="1"></a>
## Built With

### Hardware
* [Schoenhut 25 Key Piano](https://schoenhut.com/products/schoenhut-my-first-piano-ii-25-key-white)
* [Raspberry Pi 3 B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/)
* [IO Pi Plus 32-Channel Port Expander](https://www.abelectronics.co.uk/p/54/io-pi-plus)
* [Adafruit 12VDC Push-Pull Solenoid (x25)](https://www.adafruit.com/product/412)
* [Solenoid Driver Circuit](docs/)
* [Etepon 7 inch 1024x600 HDMI Display](https://www.amazon.com/gp/product/B07HMW3C7P/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1)

### Software
* [Raspbian](https://www.raspberrypi.org/documentation/raspbian/)
* [Python 3.5](https://docs.python.org/3.5/)
* [Mido](https://mido.readthedocs.io/en/latest/) - Library for working with MIDI messages and ports
* [PyQt4](http://pyqt.sourceforge.net/Docs/PyQt4/) - GUI Framework
* [Pynput](https://pynput.readthedocs.io/en/latest/) - Used to simulate and listen for keyboard inputs
* [IO Pi](https://www.abelectronics.co.uk/kb/article/23/python-library-and-demos) - Library for Raspberry Pi third party i2c expansion board

<br />

<a name="2"></a>
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Must use a Raspberry Pi running Raspbian. Install python 3 and git. Make sure everything is up-to-date including pip. Enable i2c for the IO Pi Plus expansion board by following [this guide](https://www.abelectronics.co.uk/kb/article/1/i2c--smbus-and-raspbian-linux).

### Installing

**Step 1.** Clone this repository:

```
git clone https://github.com/braydonw/pyano.git ./pyano-git
```

**Step 2.** Navigate to local project folder:

```
cd /home/pi/pyano-git
```

**Step 3.** Create a virtual environment in the project folder and then activate it:

```
python3 -m venv venv

source venv/bin/activate
```

Now you should have (venv) at the beginning of your terminal line.

**Step 4.** Install all necessary packages from requirements file:

```
pip install -r requirements.txt
```

**Side Note.** Update requirements after installing new packages:

```
pip freeze > requirements.txt
```

### Running

Run project from pyano-git directory:

```
python -m pyano
```

<br />

<a name="3"></a>
## Contributing

**Step 1.** Navigate to local project folder:

This was for my group members when the project was still ongoing.

```
cd /home/pi/pyano-git
```

**Step 2.** See what files have been modified:

```
git status
```

**Step 3.** Make a commit:

```
git add .

git commit -a -m "write commit message here"

git pull origin master

git push origin master
```

Always make a pull before a push to ensure your local project has the most up-to-date git repo files. 

**Step 4.** Remove local project directory:

```
cd /home/pi

rm -rf pyano-git
```

For more git information such as branching and merging watch [this video](https://www.youtube.com/watch?v=HVsySz-h9r4&frags=pl%2Cwn).

<br />

<a name="4"></a>
## Project Team

* **Adan Chavez** - *Software*
* **James Day** - *Hardware*
* **Camilo Rincon** - *Hardware*
* **Braydon Westmoreland** - *Software*

<br />

<a name="5"></a>
## GANNT Chart

![GANNT Chart](docs/gannt.jpg?raw=true "Week 7 GANNT Chart")

<br />

<a name="6"></a>
## License

This project is licensed under the MIT License - see the [LICENSE](docs/LICENSE) file for details.
