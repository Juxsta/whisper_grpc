import logging
from grpclib.utils import graceful_exit
from grpclib.server import Server
from .service import WhisperHandler

async def serve_grpc(host, port):
    server = Server([WhisperHandler()])
    with graceful_exit([server]):
        await server.start(host, port)
        logging.info(f'gRPC server started at {host}:{port}')
        await server.wait_closed()