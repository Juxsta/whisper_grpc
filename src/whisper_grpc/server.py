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
import asyncio
import logging
import os
import signal
import sys
from threading import Thread
from whisper_grpc import __version__
from whisper_grpc.grpc.grpc_server import serve_grpc
from whisper_grpc.rest.rest_server import serve_rest
from whisper_grpc.utils.logging_config import *
from dotenv import load_dotenv


load_dotenv()

_logger = logging.getLogger(__name__)
__author__ = "Juxsta"
__copyright__ = "Juxsta"
__license__ = "MIT"

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_logger = logging.getLogger(__name__)

verbose = os.getenv("VERBOSE")
very_verbose = os.getenv("VERY_VERBOSE")
grpc_host = os.getenv("HOST", "127.0.0.1")
grpc_port = int(os.getenv("GRPC_PORT", "50051"))
rest_host = os.getenv("HOST", "127.0.0.1")
rest_port = int(os.getenv("REST_PORT", "50052"))


def checkTruthy(string: str or None):
    try:
        if string.lower() == "true":
            return True
        elif int(string) > 0:
            return True
    except Exception as e:
        pass
    return False


# ---- CLI ----


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


async def shutdown():
    _logger.info("Received shutdown signal. Closing servers...")
    await asyncio.gather(
        grpc_server.stop(0),
        loop.run_in_executor(None, http_server.stop)
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
    setup_logging(args)
    _logger.debug("Starting servers...")

    global loop, grpc_server, http_server
    loop = asyncio.get_running_loop()
    grpc_server = serve_grpc(args.host, args.grpc_port)
    http_server = Thread(target=serve_rest, args=(args.host, args.rest_port), daemon=True)
    http_server.start()

    _logger.info(f"GRPC server started at {args.host}:{args.grpc_port}")
    _logger.info(f"REST server started at {args.host}:{args.rest_port}")

    try:
        # Use a low level API to handle signals properly
        loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(shutdown()))
        loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown()))
    except NotImplementedError:
        # Windows platform raises an exception when signals are not implemented
        pass

    await grpc_server

    _logger.info("Servers ended")
    
def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    args = parse_args(sys.argv[1:])
    setup_logging(args)

    _logger.debug("Starting servers...")
    _logger.debug(f"GRPC server running on {args.host}:{args.grpc_port}")
    _logger.debug(f"REST server running on {args.host}:{args.rest_port}")

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(sys.argv[1:]))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

