# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: whisper_grpc/grpc/proto/whisper.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%whisper_grpc/grpc/proto/whisper.proto\"\x9b\x01\n\x1eLocalTranscribeAnimeDubRequest\x12\r\n\x05title\x18\x01 \x01(\t\x12\x0c\n\x04show\x18\x02 \x01(\t\x12\x0e\n\x06season\x18\x03 \x01(\t\x12\x0f\n\x07\x65pisode\x18\x04 \x01(\t\x12\x15\n\x05model\x18\x05 \x01(\x0e\x32\x06.Model\x12\x16\n\tmax_after\x18\x06 \x01(\x05H\x00\x88\x01\x01\x42\x0c\n\n_max_after\"/\n\x1fLocalTranscribeAnimeDubResponse\x12\x0c\n\x04text\x18\x01 \x01(\t*\x82\x01\n\x05Model\x12\x08\n\x04TINY\x10\x00\x12\x08\n\x04\x42\x41SE\x10\x01\x12\t\n\x05SMALL\x10\x02\x12\n\n\x06MEDIUM\x10\x03\x12\t\n\x05LARGE\x10\x04\x12\x0c\n\x08LARGE_V2\x10\x05\x12\x0b\n\x07TINY_EN\x10\x06\x12\x0b\n\x07\x42\x41SE_EN\x10\x07\x12\x0c\n\x08SMALL_EN\x10\x08\x12\r\n\tMEDIUM_EN\x10\t2i\n\x07Whisper\x12^\n\x17LocalTranscribeAnimeDub\x12\x1f.LocalTranscribeAnimeDubRequest\x1a .LocalTranscribeAnimeDubResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'whisper_grpc.grpc.proto.whisper_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _MODEL._serialized_start=249
  _MODEL._serialized_end=379
  _LOCALTRANSCRIBEANIMEDUBREQUEST._serialized_start=42
  _LOCALTRANSCRIBEANIMEDUBREQUEST._serialized_end=197
  _LOCALTRANSCRIBEANIMEDUBRESPONSE._serialized_start=199
  _LOCALTRANSCRIBEANIMEDUBRESPONSE._serialized_end=246
  _WHISPER._serialized_start=381
  _WHISPER._serialized_end=486
# @@protoc_insertion_point(module_scope)