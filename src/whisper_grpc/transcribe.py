import logging
import magic
import tempfile
import os
from pathlib import Path
import subprocess
from pyannote.audio import Inference
import ffmpeg
import whisperx
from whisperx.utils import write_srt

hf_token = os.getenv("HF_TOKEN")
device = 'cuda'

def rip_audio_file(input_file: str, output_file: str):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-map', '0:a:0',
        '-c:a', 'pcm_s16le',
        '-metadata:s:a:0', 'language=eng',
        output_file
    ]
    subprocess.run(command)


def save_results(result, output_path):
    with open(output_path, "w", encoding="utf-8") as srt:
        write_srt(result["segments"], file=srt)


def validate_file(file: str):
    if not os.path.isfile(file):
        return False
    file_type = magic.from_file(file, mime=True)
    if not file_type.startswith('audio/') and not file_type.startswith('video/'):
        return False
    return True


def transcribe(whisper_model: whisperx.Whisper, audio_rip_path: str, logger: logging.Logger):
    try:
        logger.info("Attempting VAD")
        if not hf_token:
            raise Exception("No HF_TOKEN set")
        vad_pipeline = Inference(
            "pyannote/segmentation", pre_aggregation_hook=lambda segmentation: segmentation, use_auth_token=hf_token)
        return whisperx.transcribe_with_vad(
            whisper_model, audio_rip_path, vad_pipeline)
    except:
        logger.warning("VAD failed, falling back to non-VAD transcribe")
        return whisper_model.transcribe(
            audio_rip_path, beam_size=5, best_of=5, language="en", verbose=False)

    # Refactor the above code to remove the duplication


def transcribe_file(file: str, model: str, logging_level=logging.WARNING):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging_level)
    logger.debug(f'Transcribing {file} with model {model}')
    
    # Check if the file is valid
    output_path = Path(file).with_suffix('.en.srt')
    if output_path.exists():
        logger.warning(f'Skipping {file} - external subtitles already exist')
        return "Subtitles already exist"

    if not validate_file(file):
        logger.error(f'Skipping {file} - not a valid file')
        raise ValueError(f'Not a valid file: {file}')

    whisper_model = whisperx.load_model(model, device)
    
    # Create a temporary directory to store the ripped audio file
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            audio_rip_path = f'{tmpdir}/{os.path.basename(file)}.wav'
            rip_audio_file(file, audio_rip_path)
            # Perform the transcription
            result = transcribe(whisper_model, audio_rip_path, logger)
            # Perform the alignment
            align_model, align_metadata = whisperx.load_align_model(
                'en', device)
            result_aligned = whisperx.align(
                result["segments"], align_model, align_metadata, audio_rip_path, device)
        except ffmpeg.Error as e:
            logger.error(
                f'No English audio track found in {file}, error: {e.stderr}')
            raise ValueError(f'No English audio track found in {file}')
    # Write the results to the output file
    save_results(result_aligned, output_path)
    return f"Transcribed {file} to {output_path}"

