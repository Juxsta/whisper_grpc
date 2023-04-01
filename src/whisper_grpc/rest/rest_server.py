from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from gevent.event import Event
from whisper_grpc.utils.logging_config import *
from whisper_grpc.service import WhisperHandler
import asyncio

app = Flask(__name__)

handler = WhisperHandler()
_logger = logging.getLogger(__name__)


@app.route("/transcribe", methods=["POST"])
def transcribe():
    _logger = logging.getLogger(__name__)
    data = request.json
    _logger.debug(f"Received request: {data}")
    try:
        title = data['title']
        show = data['show']
        season = data['season']
        episode = data['episode']
        model = data['model']
        max_after = data.get('max_after', None)
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400
    _logger.info(f"Transcribing {title} {show} {season} {episode} {model} {max_after}")
    async_result = handler.LocalTranscribeAnimeDub(title=title, show=show, season=season, episode=episode, model=model, max_after=max_after)

    return jsonify({"message": "Transcription started"}), 202


def serve_rest(host, port):
    http_server = WSGIServer((host, port), app)
    http_server.start()
    _logger.info(f'Rest server started at {host}:{port}')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    stop_event = Event()

    async def stop_server():
        http_server.stop()
        stop_event.set()

    async def run_server():
        await loop.run_in_executor(None, http_server.start)
        await stop_event.wait()

    loop.run_until_complete(run_server())

    _logger.info("Rest server stopped")

    return http_server, app

