# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: whisper.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rwhisper.proto\"E\n\x1eLocalTranscribeAnimeDubRequest\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x15\n\x05model\x18\x02 \x01(\x0e\x32\x06.Model\"/\n\x1fLocalTranscribeAnimeDubResponse\x12\x0c\n\x04text\x18\x01 \x01(\t*t\n\x05Model\x12\x08\n\x04TINY\x10\x00\x12\x08\n\x04\x42\x41SE\x10\x01\x12\t\n\x05SMALL\x10\x02\x12\n\n\x06MEDIUM\x10\x03\x12\t\n\x05LARGE\x10\x04\x12\x0b\n\x07TINY_EN\x10\x05\x12\x0b\n\x07\x42\x41SE_EN\x10\x06\x12\x0c\n\x08SMALL_EN\x10\x07\x12\r\n\tMEDIUM_EN\x10\x08\x32i\n\x07Whisper\x12^\n\x17LocalTranscribeAnimeDub\x12\x1f.LocalTranscribeAnimeDubRequest\x1a .LocalTranscribeAnimeDubResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'whisper_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _MODEL._serialized_start=137
  _MODEL._serialized_end=253
  _LOCALTRANSCRIBEANIMEDUBREQUEST._serialized_start=17
  _LOCALTRANSCRIBEANIMEDUBREQUEST._serialized_end=86
  _LOCALTRANSCRIBEANIMEDUBRESPONSE._serialized_start=88
  _LOCALTRANSCRIBEANIMEDUBRESPONSE._serialized_end=135
  _WHISPER._serialized_start=255
  _WHISPER._serialized_end=360
# @@protoc_insertion_point(module_scope)