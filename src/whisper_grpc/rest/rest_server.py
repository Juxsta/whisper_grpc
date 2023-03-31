from flask import Flask, request, jsonify
from whisper_grpc.utils.logging_config import *
from whisper_grpc.service import WhisperHandler

app = Flask(__name__)

handler = WhisperHandler()

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
    app.run(host=host, port=port)

