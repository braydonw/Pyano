# Pyano Project

The Pyano is a 25-key self-playing piano powered by a Raspberry Pi using python and the MIDI file format. There are currently three modes of operation. The *player* mode is used to playback any files in the midi-files folder on the miniature piano using a series of push-pull solenoids. The *maker* mode is used to create custom MIDI files using a standard qwerty keyboard and save them to the midi-files folder. The *live* mode removes the need for MIDI files altogether and allows for a direct connection between qwerty keyboard inputs and solenoid ouputs on the miniature piano.

> Created for: <br />
> Texas Tech University <br />
> Dept. of Electrical & Computer Engineering <br />
> Project Lab II <br />
> Spring 2019 <br />

![Alt text](docs/for-readme/temp.jpg?raw=true "Week 7 GANNT Chart")

## Table of Contents
- [Built With](#1)
- [Getting Started](#2)
- [Contributing](#3)
- [Project Team](#4)
- [GANNT Chart](#5)
- [License](#6)

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
* [Pynput](https://pynput.readthedocs.io/en/latest/) - For simulating keyboard inputs in the GUI
* [IO Pi](https://www.abelectronics.co.uk/kb/article/23/python-library-and-demos) - Library for Raspberry Pi third party i2c expansion board

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

Update requirements after installing new packages:

```
$ pip freeze > requirements.txt
```

### Running

Run project from pyano-git directory:

```
python -m pyano
```

End with an example (gifs) of getting some data out of the system or using it for a little demo

<a name="3"></a>
## Contributing

**Step 1.** See what files have been modified:

```
git status
```

**Step 2.** Make a commit:

```
git commit -a
- Enter your commit message, then ctrl+X, then Enter

git pull origin master
- If everything is up-to-date press ctrl+X, then Enter

git push origin master
- Enter your username and password
```

Always make a pull before a push to ensure your local project has the most up-to-date git repo files. 

**Step 3.** Remove local project directory:

```
cd /home/pi
rm -rf pyano-git
```

For more git information such as branching and merging watch [this video](https://www.youtube.com/watch?v=HVsySz-h9r4&frags=pl%2Cwn).

<a name="4"></a>
## Project Team

* **Adan Chavez** - *Software*
* **James Day** - *Hardware*
* **Camilo Rincon** - *Hardware*
* **Braydon Westmoreland** - *Software*

<a name="5"></a>
## GANNT Chart

### Week 7 of 13

![Alt text](docs/gannt-charts/week7.jpg?raw=true "Week 7 GANNT Chart")

<a name="6"></a>
## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.
