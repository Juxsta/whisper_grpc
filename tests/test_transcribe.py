
import pytest
import os
import logging
import tempfile
import ffmpeg

from pathlib import Path

import whisperx
from pyannote.audio import Inference
from whisper_grpc.transcribe import rip_audio_file, validate_file, transcribe, transcribe_file, save_results
@pytest.fixture
def whisper_model():
    return whisperx.load_model('large-v2', 'cuda')

@pytest.fixture
def vad_pipeline():
    hf_token = os.getenv("HF_TOKEN")
    return Inference("pyannote/segmentation", pre_aggregation_hook=lambda segmentation: segmentation, use_auth_token=hf_token)

@pytest.fixture
def align_model_metadata():
    return whisperx.load_align_model('en', 'cuda')

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    return logger

def test_rip_audio_file(temp_dir):
    input_file = '../media/fate-test.mkv'
    output_file = f'{temp_dir}/fate-test.wav'
    rip_audio_file(input_file, output_file)
    assert os.path.exists(output_file)

def test_validate_file(temp_dir):
    valid_file = '../media/fate-test.mkv'
    invalid_file = '../media/invalid-file.txt'
    assert validate_file(valid_file) == True
    assert validate_file(invalid_file) == False

def test_transcribe_with_vad(whisper_model, vad_pipeline, temp_dir):
    input_file = '../media/fate-test.mkv'
    audio_rip_path = f'{temp_dir}/fate-test.wav'
    rip_audio_file(input_file, audio_rip_path)
    result = transcribe(whisper_model, audio_rip_path, vad_pipeline)
    assert result != None

def test_transcribe_without_vad(whisper_model, temp_dir):
    input_file = '../media/fate-test.mkv'
    audio_rip_path = f'{temp_dir}/fate-test.wav'
    rip_audio_file(input_file, audio_rip_path)
    result = whisper_model.transcribe(
            audio_rip_path, beam_size=5, best_of=5, language="en", verbose=False)
    assert result != None


def test_transcribe_file(temp_dir):
    input_file = '../media/fate-test.mkv'
    output_path = Path(input_file).with_suffix('.en.ass')
    if output_path.exists():
        output_path.unlink()
    result = transcribe_file(input_file, 'model.whisper', logging.WARNING)
    assert result == f"Transcribed {input_file} to {output_path}"
    assert os.path.exists(output_path)