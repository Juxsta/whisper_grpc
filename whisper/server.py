import grpc
import proto.whisper_pb2_grpc as whisper_pb2_grpc
import concurrent.futures as futures
import argparse
import logging
from service import WhisperHandler


def main(args):
    if args.very_verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    logging.info(
        f'Logging level: {logging.getLevelName(logging.getLogger().getEffectiveLevel())}')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    whisper_pb2_grpc.add_WhisperServicer_to_server(WhisperHandler(
        logging_level=logging.getLogger().getEffectiveLevel()), server)
    server.add_insecure_port('[::]:50051')
    logging.info('Starting server...')
    server.start()
    logging.info('Server started')
    try:
        server.wait_for_termination()
    except InterruptedError:
        logging.info('Received interrupt, shutting down')
        server.stop(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--very-verbose', '-vv',
                        action='store_true', help='Enable very verbose logging')
    args = parser.parse_args()
    main(args)
