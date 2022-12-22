import asyncio
import concurrent.futures
import logging
import grpc
import proto.whisper_pb2_grpc as whisper_pb2_grpc
from transcribe import transcribe_file
from proto.whisper_pb2 import LocalTranscribeAnimeDubRequest, LocalTranscribeAnimeDubResponse
from common import MODEL_MAP


class WhisperHandler (whisper_pb2_grpc.WhisperServicer):
    def __init__(self, logging_level=logging.WARNING):
        self.logging_level = logging_level
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        # Create a logger with the same name as the class
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.logging_level)

    async def LocalTranscribeAnimeDub(self, request: LocalTranscribeAnimeDubRequest, context) -> LocalTranscribeAnimeDubResponse:
        try:
            model = MODEL_MAP[request.model]
        except KeyError:
            # Return an error to the client
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid model: {request.model}")
            response =  LocalTranscribeAnimeDubResponse()
            yield response
            return
            
        # Log a message when the task is received
        self.logger.info(f"Task received: Path: {request.path}, Model: {model}")
        # Return a message to the client that the task was received
        response = LocalTranscribeAnimeDubResponse(text=f"Task received for {request.path}")
        yield response

        # Process the task asynchronously

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, transcribe_file, request.path, model, False)

        # Return the result to the client
        response = LocalTranscribeAnimeDubResponse(text=result)
        yield response