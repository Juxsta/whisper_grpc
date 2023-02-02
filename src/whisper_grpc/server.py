"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         whisper_server = whisper.main:run

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
from whisper_grpc import __version__
import os

__author__ = "Juxsta"
__copyright__ = "Juxsta"
__license__ = "MIT"

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
port = int(os.getenv("PORT")) if os.getenv("PORT") else None

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
    parser.add_argument('--port', '-p', type=int, default=50051)
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--very-verbose', '-vv',
                        action='store_true', help='Enable very verbose logging')
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


async def main(args):
    """Wrapper allowing :func:`run` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`run`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting server...")
    import asyncio
    from .service import WhisperHandler
    from grpclib.utils import graceful_exit
    from grpclib.server import Server
    server = Server([WhisperHandler(logging_level=logging.getLogger().getEffectiveLevel())])
    with graceful_exit([server]):
        await server.start(host=host if host else args.host, port=port if port else args.port)
        logging.info('Server started')
        await server.wait_closed()
        logging.info('Server closed')
    _logger.info("Server ends here")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


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