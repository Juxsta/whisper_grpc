import logging
import magic
import tempfile
import whisperx
import os
from pathlib import Path
import subprocess
from pyannote.audio import Inference
import ffmpeg


hf_token = os.getenv("HF_TOKEN")
device = 'cuda'


def transcribe_file(file: str, model: str, logging_level=logging.WARNING):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging_level)
    logger.debug(f'Transcribing {file} with model {model}')
    output_path = Path(file).with_suffix('.en.ass')
    if output_path.exists():
        logger.warning(f'Skipping {file} - external subtitles already exist')
        return "Subtitles already exist"
    if not os.path.isfile(file):
        logger.error(f'Skipping {file} - not a file')
        raise ValueError(f'Not a file: {file}')
    file_type = magic.from_file(file, mime=True)
    if file_type.startswith('audio/') or file_type.startswith('video/'):
        logger.info(f'Transcribing {file}')
        whisper_model = whisperx.load_model(model, device)
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                audio_rip_path = f'{tmpdir}/{os.path.basename(file)}.wav'
                transcribe_audio_file(file, audio_rip_path)
                logger.info(f'Transcribing {audio_rip_path}')

                vad_pipeline = Inference(
                    "pyannote/segmentation", pre_aggregation_hook=lambda segmentation: segmentation, use_auth_token=hf_token) if hf_token else None
                result = whisperx.transcribe_with_vad(
                    whisper_model, audio_rip_path, vad_pipeline) if vad_pipeline else whisper_model.transcribe(
                    audio_rip_path, beam_size=5, best_of=5, language="en", verbose=logging_level <= logging.INFO)
                align_model, align_metadata = whisperx.load_align_model(
                    'en', device)
                result_aligned = whisperx.align(
                    result["segments"], align_model, align_metadata, audio_rip_path, device,)
            except ffmpeg.Error as e:
                logger.error(
                    f'No English audio track found in {file}, error: {e.stderr}')
                raise ValueError(f'No English audio track found in {file}')
        save_results(result_aligned, output_path)
        return f"Transcribed {file} to {output_path}"
    else:
        logger.error(f'Unsupported file type: {file_type}')
        raise ValueError(f'Unsupported file type: {file_type}')


def transcribe_audio_file(input_file: str, output_file: str):
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
    with open(output_path, "w", encoding="utf-8") as ass:
        whisperx.write_ass(result["segments"], file=ass, resolution='char')
