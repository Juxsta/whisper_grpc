"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
        whisper_server = whisper_grpc.server:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``whisper_server`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import logging
import sys
import os
import asyncio
from whisper_grpc import __version__
from .grpc_server import serve_grpc
from .rest_server import serve_rest

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

_logger = logging.getLogger(__name__)
__author__ = "Juxsta"
__copyright__ = "Juxsta"
__license__ = "MIT"

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

_logger = logging.getLogger(__name__)


def checkTruthy(string:str or None):
    try:
        if string.lower() == "true":
            return True
        elif int(string) > 0:
            return True
    except Exception as e:
        pass
    return False

verbose = checkTruthy(os.getenv("VERBOSE"))
very_verbose = checkTruthy(os.getenv("VERY_VERBOSE"))
host = os.getenv("HOST")
grpc_port = int(os.getenv("GRPC_PORT")) if os.getenv("GRPC_PORT") else None
rest_port = int(os.getenv("REST_PORT")) if os.getenv("REST_PORT") else None
# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Whisper Server")
    parser.add_argument(
        "--version",
        action="version",
        version=f"whisper {__version__}",
    )
    parser.add_argument('--host', '-H', default='127.0.0.1')
    parser.add_argument('--grpc-port', '-gp', default=50051, type=int)
    parser.add_argument('--rest-port', '-rp', default=50052, type=int)
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--very-verbose', '-vv',
                        action='store_true', help='Enable very verbose logging')
    return parser.parse_args(args)


def setup_logging(args):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    if args.very_verbose or very_verbose:
        _logger.setLevel(logging.DEBUG)
        
    elif args.verbose or verbose:
        _logger.setLevel(logging.INFO)
    else:
        _logger.setLevel(logging.WARNING)


async def main(args):
    """Wrapper allowing :func:`run` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`run`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args)
    _logger.debug("Starting servers...")

    grpc_host, grpc_port = args.host, args.grpc_port
    rest_host, rest_port = args.host, args.rest_port

    grpc_server = serve_grpc(grpc_host, grpc_port)
    rest_server = asyncio.to_thread(serve_rest, rest_host, rest_port)

    await asyncio.gather(grpc_server, rest_server)

    _logger.info("Servers end here")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    asyncio.run(main(sys.argv[1:]))


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m whisper.main
    #
    run()