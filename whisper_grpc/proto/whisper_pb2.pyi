from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

BASE: Model
BASE_EN: Model
DESCRIPTOR: _descriptor.FileDescriptor
LARGE: Model
MEDIUM: Model
MEDIUM_EN: Model
SMALL: Model
SMALL_EN: Model
TINY: Model
TINY_EN: Model

class LocalTranscribeAnimeDubRequest(_message.Message):
    __slots__ = ["episode", "max_after", "model", "season", "show", "title"]
    EPISODE_FIELD_NUMBER: _ClassVar[int]
    MAX_AFTER_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SEASON_FIELD_NUMBER: _ClassVar[int]
    SHOW_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    episode: str
    max_after: int
    model: Model
    season: str
    show: str
    title: str
    def __init__(self, title: _Optional[str] = ..., show: _Optional[str] = ..., season: _Optional[str] = ..., episode: _Optional[str] = ..., model: _Optional[_Union[Model, str]] = ..., max_after: _Optional[int] = ...) -> None: ...

class LocalTranscribeAnimeDubResponse(_message.Message):
    __slots__ = ["text"]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class Model(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
