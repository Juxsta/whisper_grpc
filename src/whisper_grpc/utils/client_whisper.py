import grpc
from whisper_grpc.proto.whisper_pb2 import LocalTranscribeAnimeDubRequest
from whisper_grpc.proto.whisper_pb2_grpc import WhisperStub
import logging
import asyncio

class ClientWhisper:
    """This client is deprecated """
    def __init__(self, host, port, logging_level=logging.WARNING):
        self.host = host
        self.port = port
        self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = WhisperStub(self.channel)
        self.transcribe_tasks = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging_level)

    async def transcribe(self, directory, model):
        # Send the request to the server
        self.logger.debug(f"Transcribing {directory} with model {model}")
        request = LocalTranscribeAnimeDubRequest(path=directory, model=model)

        # Stream the response asynchronously
        loop = asyncio.get_event_loop()
        response_stream = self.stub.LocalTranscribeAnimeDub.async_stream(
            request,
            loop=loop
        )
        task = asyncio.create_task(self._process_response_stream(response_stream))
        self.transcribe_tasks.append(task)

    async def _process_response_stream(self, response_stream):
        responses = []
        async for response in response_stream:
            self.logger.info(f"Received response: {response.text}")
            responses.append(response)
        return responses

    async def wait_for_transcribe_tasks(self):
        self.logging.debug("Waiting for transcribe tasks to complete")
        await asyncio.gather(*self.transcribe_tasks)
        self.logging.debug("All transcribe tasks completed")

    def close(self):
        self.logger.debug("Closing channel")
        self.channel.close()