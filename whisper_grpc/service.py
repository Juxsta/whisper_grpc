import asyncio
import concurrent.futures
import logging
import grpc
import os
import proto.whisper_grpc as whisper_grpc
from transcribe_anime_episode import transcribe_file
from proto.whisper_pb2 import LocalTranscribeAnimeDubRequest, LocalTranscribeAnimeDubResponse
from common import MODEL_MAP
from utils.client_plex import ClientPlexServer

plex_url = os.getenv("PLEX_URL", "http://plex:32400")
plex_token = os.getenv("PLEX_TOKEN", "avc")
transcribe_timeout = os.getenv("TRANSCRIBE_TIMEOUT", 30) * 60 #in minutes
class WhisperHandler (whisper_grpc.WhisperBase):
    def __init__(self, max_concurrent_transcribes=4, logging_level=logging.WARNING):
        self.max_concurrent_tasks = max_concurrent_transcribes
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_tasks)
        self.semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging_level)
        
    async def submit_task(self, file, model, verbose):
        async with self.semaphore:
            task = self.executor.submit(transcribe_file, file, model, verbose)
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
        stream.send_initial_metadata([('grpc-status', '0')])
        self.logger.info(f"LocalTranscribeAnimeDub: {request}")
        try:
            model = MODEL_MAP[request.model]
        except KeyError:
            # Return an error to the client
            stream.send_initial_metadata([('grpc-status', '3')])
            stream.set_trailing_metadata([('grpc-status-details-bin', 'Invalid model')])
            self.logger.error(f"Invalid model: {request.model}")
            return

        try:
            plex = ClientPlexServer(plex_url, plex_token, request.title, request.show, request.season, request.episode, log_level=self.logger.getEffectiveLevel())
        except Exception as e:
            stream.send_initial_metadata([('grpc-status', '3')])
            stream.set_trailing_metadata([('grpc-status-details-bin', f'Unable to find requested title: {request.title}  Error: {e}')])
            self.logger.error(f"Unable to find requested title: {request.title}  Error: {e}")
            return
        if not plex.is_anime():
            stream.send_initial_metadata([('grpc-status', '3')])
            stream.set_trailing_metadata([('grpc-status-details-bin', f'Title is not an anime: {request.title}')])
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
                stream.send_initial_metadata([('grpc-status', '3')])
                stream.set_trailing_metadata([('grpc-status-details-bin', f'Unable to find requested episode: {request.title}  Error: {e}')])
                return
            pass
        # Transcribe the episodes in episodes_to_transcribe
        self.logger.info(f"Transcribing {len(episodes_to_transcribe)} episodes")
        tasks = map(lambda x: self.submit_task(x, model, request.verbose), episodes_to_transcribe)
        for task in asyncio.as_completed(tasks): 
            response = LocalTranscribeAnimeDubResponse()
            try:
                response.message = await task
                self.logger.info(f"Succes")
                await stream.send_message(response)
            except Exception as e:
                self.logger.error(f"Failed")
                response.message = f"Failed: {e}"
                await stream.send_message(response)
        stream.set_trailing_metadata([('grpc-status-details-bin', 'Success')])
        return