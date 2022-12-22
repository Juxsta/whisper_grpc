from proto.whisper_pb2 import Model

MODEL_MAP = {
    Model.TINY: "tiny",
    Model.BASE: "base",
    Model.SMALL: "small",
    Model.MEDIUM: "medium",
    Model.LARGE: "large",
    Model.TINY_EN: "tiny.en",
    Model.BASE_EN: "base.en",
    Model.SMALL_EN: "small.en",
    Model.MEDIUM_EN: "medium.en",
}

def model_from_string(model_string: str) -> Model:
    return {v: k for k, v in MODEL_MAP.items()}[model_string]

def model_to_string(model: Model) -> str:
    return MODEL_MAP[model]