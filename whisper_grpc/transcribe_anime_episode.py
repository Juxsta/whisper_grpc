import argparse
from grpclib.client import Channel
from proto.whisper_pb2 import LocalTranscribeAnimeDubRequest
from common import MODEL_MAP, model_from_string
from proto.whisper_grpc import WhisperBase
from proto.whisper_pb2 import LocalTranscribeAnimeDubRequest, LocalTranscribeAnimeDubResponse
import asyncio

async def main():
    async with Channel('whisper-grpc', 50051) as channel:
        stub = WhisperBase(channel)
        request = LocalTranscribeAnimeDubRequest(
            title=args.title,
            show=args.show,
            season=args.season,
            episode=args.episode,
            model=model_from_string(args.model)
        )
        async for response in stub.LocalTranscribeAnimeDub(request):
            print(response)

# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--title', required=True, help='Title of the media to transcribe')
parser.add_argument('--show', required=True, help='Show of the media to transcribe')
parser.add_argument('--season', required=True, help='Season of the media to transcribe')
parser.add_argument('--episode', required=True, help='Episode of the media to transcribe')
parser.add_argument('--model', help='Model to use for transcribing', default='BASE_EN', type=str, choices=MODEL_MAP.values())
args = parser.parse_args()
asyncio.run(main())