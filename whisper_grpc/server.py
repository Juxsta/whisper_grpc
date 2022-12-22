import grpc
import concurrent.futures as futures
import argparse
import logging
from service import WhisperHandler
import asyncio
from grpclib.utils import graceful_exit
from grpclib.server import Server
import os

def checkTruthy(string:str or None):
    if string:
        if string.lower() == "true":
            return True
        elif int(string) > 0:
            return True
    return False
verbose = checkTruthy(os.getenv("VERBOSE"))
very_verbose = checkTruthy(os.getenv("VERY_VERBOSE"))

async def main(args):
    if args.very_verbose or very_verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose or verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    logging.info(
        f'Logging level: {logging.getLevelName(logging.getLogger().getEffectiveLevel())}')
    server = Server([WhisperHandler(logging_level=logging.getLogger().getEffectiveLevel())])
    with graceful_exit([server]):
        await server.start(args.host, args.port)
        logging.info('Server started')
        await server.wait_closed()
        logging.info('Server closed')
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', '-H', default='localhost')
    parser.add_argument('--port', '-p', type=int, default=50051)
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--very-verbose', '-vv',
                        action='store_true', help='Enable very verbose logging')
    args = parser.parse_args()
    asyncio.run(main(args))
