import asyncio
import concurrent.futures
import logging
import os
import whisper_grpc.proto.whisper_grpc as whisper_grpc
from whisper_grpc.proto.whisper_pb2 import LocalTranscribeAnimeDubResponse
from .common import MODEL_MAP
from whisper_grpc.utils.client_plex import ClientPlexServer
from .transcribe import transcribe_file
from grpclib import Status
from plexapi.video import Episode
plex_url = os.getenv("PLEX_URL", "http://plex:32400")
plex_token = os.getenv("PLEX_TOKEN")
max_concurrent_transcribes = int(os.getenv("MAX_CONCURRENT_TRANSCRIBES", 4))
transcribe_timeout = os.getenv("TRANSCRIBE_TIMEOUT", 30) * 60 #in minutes
class WhisperHandler (whisper_grpc.WhisperBase):
    def __init__(self, logging_level=logging.WARNING):
        self.max_concurrent_tasks = max_concurrent_transcribes
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_tasks)
        self.semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging_level)
        
    async def submit_task(self, file:str, model:str, episode:Episode = None):
        """
        Submit a task to the executor and return the result.
        Episode is optional, and is only used as a helper to refresh episode metadata upon transcription completion.
        """
        async with self.semaphore:
            task = self.executor.submit(transcribe_file, file, model,self.logger.getEffectiveLevel())
            try:
                result = await asyncio.wrap_future(task)
                self.logger.info(f"Transcription complete: {result}")
                if episode is not None:
                    self.logger.info(f"Refreshing episode metadata {episode.title}")
                    episode.refresh()
                return f"Transcription for file {file} complete: {result}"
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
            await stream.send_trailing_metadata(status=Status.NOT_FOUND, status_message=f'Unable to find requested title: {request.title}  Error: {e}')
            self.logger.error(f"Unable to find requested title: {request.title}  Error: {e}")
            return
        if not plex.is_anime():
            await stream.send_trailing_metadata(status=Status.INVALID_ARGUMENT, status_message=f'Title is not an anime: {request.title}')
            self.logger.error(f"Title is not an anime: {request.title}")
            return

        # Process the transcription tasks asynchronously
        episodes_to_transcribe:list[Episode] = []
        try:
            for i in range(request.max_after + 1 if request.max_after else 1):
                episodes_to_transcribe.append(plex.get_episode())
                plex.set_next_episode()
        except Exception as e:
            if len(episodes_to_transcribe == 0):
                await stream.send_trailing_metadata(status=Status.NOT_FOUND, status_message=f'Unable to find any episodes for title: {request.title}  Error: {e}')
                return
            pass
        # Transcribe the episodes in episodes_to_transcribe
        self.logger.info(f"Transcribing {len(episodes_to_transcribe)} episodes: {map(lambda ep: ep.locations[0] ,episodes_to_transcribe)}")
        await stream.send_message(LocalTranscribeAnimeDubResponse(text=f"Transcribing the following episodes: {map(lambda ep: ep.locations[0] ,episodes_to_transcribe)}"))
        def map_to_task(ep:Episode):
            return self.submit_task(ep.locations[0], model, ep)
        tasks = map(map_to_task, episodes_to_transcribe)
        as_completed = asyncio.as_completed(tasks)
        for task in as_completed: 
            try:
                self.logger.info(f"Successfully transcribed this episode: {await task}")
            except Exception as e:
                self.logger.error(f"Failed")
        return
