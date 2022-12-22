import argparse
from grpclib.client import Channel
from proto.whisper_pb2 import LocalTranscribeAnimeDubRequest
from common import MODEL_MAP, model_from_string
from proto.whisper_grpc import WhisperStub
from proto.whisper_pb2 import LocalTranscribeAnimeDubRequest, LocalTranscribeAnimeDubResponse
import asyncio

async def main():
    async with Channel('whisper-grpc', 50051) as channel:
        stub = WhisperStub(channel)
        request = LocalTranscribeAnimeDubRequest(
            title=args.title,
            show=args.show,
            season=args.season,
            episode=args.episode,
            model=model_from_string(args.model)
        )
        async with stub.LocalTranscribeAnimeDub.open() as stream:
            # Send initial request
            await stream.send_message(request)
            # Recieve Responses and print them as they come in
            async for response in stream:
                print(response)
            print(await stream.recv_message())
            print(await stream.recv_trailing_metadata())
            stream.end()
            

# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--title', required=True, help='Title of the media to transcribe')
parser.add_argument('--show', required=True, help='Show of the media to transcribe')
parser.add_argument('--season', required=True, help='Season of the media to transcribe')
parser.add_argument('--episode', required=True, help='Episode of the media to transcribe')
parser.add_argument('--model', help='Model to use for transcribing', default='BASE_EN', type=str, choices=MODEL_MAP.values())
args = parser.parse_args()
asyncio.run(main())