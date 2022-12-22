import argparse
import logging
from common import MODEL_MAP, model_from_string
from client_plex import ClientPlexServer
from client_whisper import ClientWhisper
MAX_EPISODES = 4

async def main(args):
    if args.very_verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    logging.debug(args)
    try:
        plex = ClientPlexServer(args.plex_url, args.plex_token, args.show, args.season, args.episode, log_level=logging.getLogger().getEffectiveLevel())
    except Exception as e:
        logging.error(f'No media found with title "{args.title}"')
        logging.error(e)
        exit(1)
    if not plex.is_anime():
        logging.error(f'{args.show} is not an anime')
        exit(1)
    # Establish connection to the Whisper server
    whisper = ClientWhisper(args.grpc_host, args.grpc_port, log_level=logging.getLogger().getEffectiveLevel())
    #  Loop over this episode and the next MAX_EPISODES episodes and transcribe them
    try:
        for i in range(0, MAX_EPISODES):
            logging.info(f'Transcribing episode {plex.episode_number}')
            whisper.transcribe(plex.get_episode_location(), model_from_string(args.model))
            plex.next_episode()
    except Exception as e:
        logging.error(e)
    await whisper.wait_for_transcribe_tasks()
    whisper.close()
    
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
    parser.add_argument('--plex_url', help='URL of the Plex instance', default="http://plex:32400")
    parser.add_argument('--plex_token', help='Token for the Plex instance', required=True)
    parser.add_argument('--grpc_host', help='Hostname for the gRPC server', default='whisper-server')
    parser.add_argument('--grpc_port', help='Port for the gRPC server', default=50051, type=int)

    args = parser.parse_args()
    main(args)