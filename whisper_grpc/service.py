import asyncio
import concurrent.futures
import logging
import grpc
import os
import proto.whisper_pb2_grpc as whisper_pb2_grpc
from transcribe import transcribe_file
from proto.whisper_pb2 import LocalTranscribeAnimeDubRequest, LocalTranscribeAnimeDubResponse
from common import MODEL_MAP
from utils.client_plex import ClientPlexServer

plex_url = os.getenv("PLEX_URL", "http://plex:32400")
plex_token = os.getenv("PLEX_TOKEN")
class WhisperHandler (whisper_pb2_grpc.WhisperServicer):
    def __init__(self, logging_level=logging.WARNING):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        # Create a logger with the same name as the class
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging_level)

        if plex_url is None:
            self.logger.warning("PLEX_URL is not set, defaulting to http://plex:32400")
        if plex_token is None:
            self.logger.error("PLEX_TOKEN is not set")
            raise ValueError("PLEX_TOKEN is not set")

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
        try:
            plex = ClientPlexServer(plex_url, plex_token, request.title, request.show, request.season, request.episode, log_level=self.logger.getEffectiveLevel())
        except Exception as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Unable to find requested title: {request.title}  Error: {e}")
            response = LocalTranscribeAnimeDubResponse()
            yield response
            return
        if not self.plex.is_anime():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Title is not an anime: {request.title}")
            response = LocalTranscribeAnimeDubResponse()
            yield response
            return

        # Process the transcription tasks asynchronously
        loop = asyncio.get_event_loop()
        tasks = []
        # Transcribe the current episode up to request.max_after if defined
        for i in range(request.max_after + 1 if request.max_after else 1):
            try:
                episode_location = plex.get_episode_location()
                self.logger.info(f"Transcribing {episode_location} with model {model}")
                task = loop.run_in_executor(self.executor, transcribe_file, episode_location, model, False)
                tasks.append(task)
                self.plex.set_next_episode()
            except Exception as e:
                self.logger.error(f"Unable to find next episode: {e}")
                break

        # Wait for all transcription tasks to complete
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            self.logger.info(f"Transcription complete: {result}")
            results.append(result)

        # Return the results to the client
        response = LocalTranscribeAnimeDubResponse(text="Transcription tasks complete")
        yield response