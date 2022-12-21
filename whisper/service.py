import asyncio
import concurrent.futures
import proto.whisper_pb2_grpc as whisper_pb2_grpc
from transcribe import transcribe_file
from proto.whisper_pb2 import Model, LocalTranscribeAnimeDubRequest, LocalTranscribeAnimeDubResponse
from common import MODEL_MAP


class WhisperHandler (whisper_pb2_grpc.WhisperServicer):
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    async def LocalTranscribeAnimeDub(self, request: LocalTranscribeAnimeDubRequest, context) -> LocalTranscribeAnimeDubResponse:
        model = MODEL_MAP[request.model]
        # Return a message to the client that the task was received
        response = LocalTranscribeAnimeDubResponse(text="Task received")
        yield response

        # Process the task asynchronously

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, transcribe_file, request.path, model, False)

        # Return the result to the client
        response = LocalTranscribeAnimeDubResponse(text=result)
        yield response
