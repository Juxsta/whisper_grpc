import logging
import os

verbose = os.getenv("VERBOSE")
very_verbose = os.getenv("VERY_VERBOSE")
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG if very_verbose else logging.INFO if verbose else logging.WARNING,
)
