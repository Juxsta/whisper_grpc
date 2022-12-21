import whisper_pb2, whisper_pb2_grpc
from transcribe import transcribe_file

class WhisperHandler(whisper_pb2_grpc.WhisperServicer):
    def LocalTranscribe(self, request, context):
        transcribe_file(request.path, "base.en", False)
        return whisper_pb2.LocalTranscribeResponse(text="Hello, " + request.path)
    