import argparse
import ffmpeg
import plexapi
import logging
import grpc
import asyncio
from plexapi.server import PlexServer
from proto.whisper_pb2 import LocalTranscribeAnimeDubRequest
from proto.whisper_pb2_grpc import WhisperStub
from common import MODEL_MAP, model_from_string
# CONSTANTS
PLEX_URL = 'http://plex:32400'  # Replace with the actual URL of your Plex instance
# Replace with the actual token for your Plex instance
PLEX_TOKEN = 'twyXwRPWArQw6Dr12Ui4'

# function to connect to grpc server, send request and wait for response


async def transcribe(directory, model):
    # Connect to the Whisper server
    channel = grpc.insecure_channel('localhost:50051')
    stub = WhisperStub(channel)

    # Send the request to the server
    request = LocalTranscribeAnimeDubRequest(path=directory, model=model)

    # Stream the response asynchronously
    loop = asyncio.get_event_loop()
    response_stream = stub.LocalTranscribeAnimeDub.async_stream(
        request,
        loop=loop
    )
    responses = []
    async for response in response_stream:
        logging.info(f'Received response: {response.text}')
        responses.append(response)
    await asyncio.gather(*responses)


def main(args):
    if args.very_verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    logging.debug(args)

    # Connect to the Plex instance
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    # Search for the media with the given title
    try:
        show = plex.library.section("TV Shows").get(args.show)
        logging.debug(f'Found show {show}')
        season = show.season(args.season)
        logging.debug(f'Found season {season}')
        episode = season.episode(args.episode)
        logging.debug(f'Found episode {episode}')
    except plexapi.exceptions.NotFound:
        logging.error(f'No media found with title "{args.title}"')
        exit(1)

    logging.debug(f'Found {season}')
    # Only transcribe the media if show is anime
    # It is an anime if the episode has an english and japanese audio track
    logging.debug(f'location: {episode.locations}')

    location = episode.locations[0]
    video_file = ffmpeg.probe(location)
    if any(
        stream["codec_type"] == "audio" and stream["tags"]["language"] == "jpn"
        for stream in video_file["streams"]
    ):
        logging.debug(f'Found Japanese audio track')

        transcribe(episode.locations[0], model_from_string(args.model))

    else:
        logging.error(f'Skipping {args.title} - not an anime TV show')
        exit(1)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', required=True,
                        help='Title of the media to transcribe')
    parser.add_argument('--show', required=True,
                        help='Show of the media to transcribe')
    parser.add_argument('--season', required=True,
                        help='Season of the media to transcribe')
    parser.add_argument('--episode', required=True,
                        help='Episode of the media to transcribe')
    parser.add_argument('--model', help='Model to use for transcribing', default='BASE_EN', type=str, choices=MODEL_MAP.values())    
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--very-verbose', '-vv',
                        action='store_true', help='Enable very verbose logging')

    args = parser.parse_args()
    main(args)
