# FSM VHDL Generator

FSM VHDL Generator is a simple graphical tool in python3 to quickly draw a Finite State Machine and generate VHDL code for use in simulation and synthesis applications such as Xilinx and Altera.

The application currently supports Moore Finite State Machine and simple binary outputs.


## Installation

First, check that tkinter 8.6 or higher is available on your python installation:

```python
>>> import tkinter
>>> print(tkinter.TkVersion)
```

Then install the application with pip. You may wish to do this in a virtual environment:

Create the virtual environment:

```bash
python3 -m venv env
source env/bin/activate
```


## Usage

After installation, simply launch the application by name:

```bash
fsmvhdlgenerator
```

Simply select a tool and start creating! If you're ever stuck, take a look at the message bar at the bottom of the program.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

FSM VHDL Generator uses the tkinter GUI framework and depends on jinja2, boolean.py, and pygments. It uses flake8, mypy, and pydocstyle for code quality, using Google docstring conventions. Additionally, pylint is also used, though not strictly adhered to.

Please make sure to update tests as appropriate.


## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt)
