import logging
import magic
import tempfile
import whisper
import os
import ffmpeg
from whisper.utils import write_srt
from pathlib import Path
import subprocess

def transcribe_file(file: str, whisper_model: whisper.Whisper, logging_level=logging.WARNING):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging_level)
    output_path = Path(file).with_suffix('.en.srt')
    if output_path.exists():
        logger.warning(f'Skipping {file} - external subtitles already exist')
        return "Subtitles already exist"
    if not os.path.isfile(file):
        logger.error(f'Skipping {file} - not a file')
        raise ValueError(f'Not a file: {file}')
    file_type = magic.from_file(file, mime=True)
    if file_type.startswith('audio/') or file_type.startswith('video/'):
        logger.info(f'Transcribing {file}')
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                audio_rip_path =  f'{tmpdir}/{os.path.basename(file)}.wav'
                transcribe_audio_file(file, audio_rip_path)
                result = whisper_model.transcribe(audio=audio_rip_path, beam_size=5, best_of=5, decode_options={"language": "en"})
            except ffmpeg.Error as e:
                logger.error(
                    f'No English audio track found in {file}, error: {e.stderr}')
                raise ValueError(f'No English audio track found in {file}')
        save_results(result, output_path)
        return f"Transcribed {file} to {output_path}"
    else:
        logger.error(f'Unsupported file type: {file_type}')
        raise ValueError(f'Unsupported file type: {file_type}')


def transcribe_audio_file(input_file:str, output_file:str):
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
