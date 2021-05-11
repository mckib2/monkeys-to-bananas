# monkeys-to-bananas

## Environment Setup

Clone the repo:

    git clone https://github.com/mckib2/monkeys-to-bananas.git

I use `venv` for my virtual environments.  You can create one like this:

    python3 -m venv /path/to/virtual/environment

If you are on Linux, you may be prompted to install extra development
tooling and libraries like `python3.x-venv`.

To activate and deactive the environment, do this:

    # activate
    source [path to virtual environment]/bin/activate

    # deactive
    deactive

To remove the virtual environment, simply delete the directory
where you installed it.

To install all the required dependencies, use the `requirements.txt`
file in the root of the repository:

    pip install -r requirements.txt

## Starting the Server

We use Flask.  There is an included development server built in that can
be started by running the `start_server.py` script:

    python start_server.py