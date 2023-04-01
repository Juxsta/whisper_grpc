from whisper_grpc.utils.logging_config import *
from grpclib.utils import graceful_exit
from grpclib.server import Server
from ..service import WhisperHandler
_logger = logging.getLogger(__name__)

async def serve_grpc(host, port):
    server = Server([WhisperHandler()])
    with graceful_exit([server]):
        await server.start(host, port)
        logging.info(f'gRPC server started at {host}:{port}')
        await server.wait_closed()
        _logger.info("Shutdown gRPC server")