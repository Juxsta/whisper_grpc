import asyncio
import concurrent.futures
import logging
import grpc
import os
import proto.whisper_grpc as whisper_grpc
from proto.whisper_pb2 import LocalTranscribeAnimeDubResponse
from common import MODEL_MAP
from utils.client_plex import ClientPlexServer
from transcribe import transcribe_file
from grpclib import Status
import whisper
plex_url = os.getenv("PLEX_URL", "http://plex:32400")
plex_token = os.getenv("PLEX_TOKEN")
max_concurrent_transcribes = int(os.getenv("MAX_CONCURRENT_TRANSCRIBES", 4))
model = os.getenv("MODEL", "base.en")
transcribe_timeout = os.getenv("TRANSCRIBE_TIMEOUT", 30) * 60 #in minutes
class WhisperHandler (whisper_grpc.WhisperBase):
    def __init__(self, logging_level=logging.WARNING):
        self.max_concurrent_tasks = max_concurrent_transcribes
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_tasks)
        self.semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging_level)
        self.whisper = whisper.load_model(model)
        
    async def submit_task(self, file:str):
        async with self.semaphore:
            task = self.executor.submit(transcribe_file, file, self.whisper,self.logger.getEffectiveLevel())
            try:
                result = await asyncio.wrap_future(task)
                self.logger.info(f"Transcription complete: {result}")
                return "Transcription for file {file} complete: {result}"
            except Exception as e:
                self.logger.error(f"Transcription failed: {e}")
                return f"Transcription for file {file} failed: {e}"
        
    async def LocalTranscribeAnimeDub(self, stream):
        # Get the first request
        request = await stream.recv_message()
        stream.send_initial_metadata(metadata=[('grpc-status', '0')])
        self.logger.info(f"LocalTranscribeAnimeDub: {request}")
        try:
            model = MODEL_MAP[request.model]
        except KeyError:
            # Return an error to the client
            stream.send_trailing_metadata(status=Status.INVALID_ARGUMENT, status_message=f'Invalid model: {request.model}')
            self.logger.error(f"Invalid model: {request.model}")
            return

        try:
            plex = ClientPlexServer(plex_url, plex_token, request.title, request.show, request.season, request.episode, log_level=self.logger.getEffectiveLevel())
        except Exception as e:
            stream.send_trailing_metadata(status=Status.NOT_FOUND, status_message=f'Unable to find requested title: {request.title}  Error: {e}')
            self.logger.error(f"Unable to find requested title: {request.title}  Error: {e}")
            return
        if not plex.is_anime():
            stream.send_trailing_metadata(status=Status.INVALID_ARGUMENT, status_message=f'Title is not an anime: {request.title}')
            self.logger.error(f"Title is not an anime: {request.title}")
            return

        # Process the transcription tasks asynchronously
        episodes_to_transcribe = []
        try:
            for i in range(request.max_after + 1 if request.max_after else 1):
                episodes_to_transcribe.append(plex.get_episode_location())
                plex.set_next_episode()
        except Exception as e:
            if len(episodes_to_transcribe == 0):
                stream.send_trailing_metadata(status=Status.NOT_FOUND, status_message=f'Unable to find any episodes for title: {request.title}  Error: {e}')
                return
            pass
        # Transcribe the episodes in episodes_to_transcribe
        self.logger.info(f"Transcribing {len(episodes_to_transcribe)} episodes: {episodes_to_transcribe}")
        def map_to_task(ep_location:str):
            return self.submit_task(ep_location)
        tasks = map(map_to_task, episodes_to_transcribe)
        as_completed = asyncio.as_completed(tasks)
        await stream.send_message(LocalTranscribeAnimeDubResponse(text=f"Transcribing the following episodes: {episodes_to_transcribe}"))
        for task in as_completed: 
            try:
                self.logger.info(f"Successfully transcribed this episode: {await task}")
            except Exception as e:
                self.logger.error(f"Failed")
        return
