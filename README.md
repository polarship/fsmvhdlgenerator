<img src="https://github.com/polarship/fsmvhdlgenerator/raw/master/docs/logo-readme.png" width="1440">

# FSM VHDL Generator

FSM VHDL Generator is a simple graphical tool written in Python3 to quickly generate VHDL code finite state machines.

As shown below drawing finite state machines is simple and fast, allowing you to quickly generate VHDL code for use in simulation and synthesis applications such as those by Xilinx and Altera.

<img src="https://github.com/polarship/fsmvhdlgenerator/raw/master/docs/demos/demo1.gif" width="1200">

<img src="https://github.com/polarship/fsmvhdlgenerator/raw/master/docs/demos/demo2.gif" width="1200">

<img src="https://github.com/polarship/fsmvhdlgenerator/raw/master/docs/demos/demo3.gif" width="1200">

The application currently supports Moore finite state machines and simple binary outputs. In addition to the finite state machine itself, FSM VHDL Generator can generate a VHDL testbench of your finite state machine.

FSM VHDL Generator runs on the Tkinter GUI toolkit and is designed to work in Ubuntu 18.04 and its derivatives.


## Installation

First, check that tkinter 8.6 or higher is available on your Python3 installation:

```python
>>> import tkinter
>>> print(tkinter.TkVersion)
```

Then, install the application. You may wish to do this by first creating a virtual environment:

```console
$ python3 -m venv env
$ source env/bin/activate
```

Install the application as follows (though you may choose to build it instead):
```console
$ python3 setup.py install
```


## Usage

After installation, simply launch the application by name:

```console
$ fsmvhdlgenerator
```

Simply select a tool and start creating! If you're ever stuck, take a look at the message bar at the bottom of the program. It gives contextual help messages as you're using the program.


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

FSM VHDL Generator uses the tkinter GUI toolkit and depends on jinja2, boolean.py, and pygments. It uses flake8, mypy, and pydocstyle for code quality, using Google docstring conventions. Additionally, pylint is also used, though not strictly adhered to.

Please make sure to update tests as appropriate.


## License

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt)
