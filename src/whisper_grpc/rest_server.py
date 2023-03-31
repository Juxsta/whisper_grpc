# rest_server.py
from flask import Flask, request, jsonify
import logging
import os
from whisper_grpc.service import WhisperHandler

app = Flask(__name__)

handler = WhisperHandler(logging_level=logging.INFO)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.json

    try:
        title = data['title']
        show = data['show']
        season = data['season']
        episode = data['episode']
        model = data['model']
        max_after = data.get('max_after', None)
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400

    async_result = handler.LocalTranscribeAnimeDub(title=title, show=show, season=season, episode=episode, model=model, max_after=max_after)

    return jsonify({"message": "Transcription started"}), 202

def serve_rest(host, port):
    app.run(host=host, port=port)

