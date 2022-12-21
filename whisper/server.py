import grpc, proto.whisper_pb2_grpc as whisper_pb2_grpc, concurrent.futures as futures
from service import WhisperHandler

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
whisper_pb2_grpc.add_WhisperServicer_to_server(WhisperHandler(), server)
server.add_insecure_port('[::]:50051')
server.start()