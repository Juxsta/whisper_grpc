from .utils.logging_config import *
import magic
import tempfile
import os
from pathlib import Path
import subprocess
from pyannote.audio import Inference
import ffmpeg
import whisperx
from whisperx.utils import write_srt
import pysubs2

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


def transcribe(whisper_model: whisperx, audio_rip_path: str, _logger: logging.Logger):
    try:
        _logger.info("Attempting VAD")
        if not hf_token:
            raise Exception("No HF_TOKEN set")
        vad_pipeline = Inference(
            "pyannote/segmentation", pre_aggregation_hook=lambda segmentation: segmentation, use_auth_token=hf_token)
        return whisperx.transcribe_with_vad(
            whisper_model, audio_rip_path, vad_pipeline)
    except:
        _logger.warning("VAD failed, falling back to non-VAD transcribe")
        return whisper_model.transcribe(
            audio_rip_path, beam_size=5, best_of=5, language="en", verbose=False)

    # Refactor the above code to remove the duplication
    
def merge_subtitles(whisper_subtitles, forced_subs_path):
    subs = pysubs2.load(forced_subs_path, encoding="utf-8")

    for transcription in whisper_subtitles:
        start_time = pysubs2.make_time(s=transcription["start_time"])
        end_time = pysubs2.make_time(s=transcription["end_time"])
        text = transcription["text"]

        new_event = pysubs2.SSAEvent(start=start_time, end=end_time, text=text)
        subs.insert(new_event)

    subs.sort()
    return subs

def extract_forced_subtitles(video_file: str, output_path: str):
    # Get subtitle stream information using ffprobe
    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "s",
        "-show_entries", "stream=index:stream_tags=language:stream_disposition=forced",
        "-of", "csv=p=0",
        video_file
    ]
    output = subprocess.check_output(command, universal_newlines=True).strip().splitlines()
    subtitle_streams = [line.split(',') for line in output]

    # Find the first forced English subtitle stream
    forced_stream_index = None
    for stream in subtitle_streams:
        index, language, forced = stream
        if language.lower() == "eng" and forced == "1":
            forced_stream_index = index
            break

    if forced_stream_index is None:
        return False

    # Extract the forced English subtitle stream using ffmpeg
    command = [
        "ffmpeg",
        "-i", video_file,
        "-map", f"0:s:{forced_stream_index}",
        "-c:s", "copy",
        "-vn", "-an",
        "-f", "ass",
        output_path
    ]
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def transcribe_file(file: str, model: str):
    _logger = logging.getLogger(__name__)
    _logger.debug(f'Transcribing {file} with model {model}')
    
    # Check if the file is valid
    output_path = Path(file).with_suffix('.en.srt')
    if output_path.exists():
        _logger.warning(f'Skipping {file} - external subtitles already exist')
        return "Subtitles already exist"

    if not validate_file(file):
        _logger.error(f'Skipping {file} - not a valid file')
        raise ValueError(f'Not a valid file: {file}')

    whisper_model = whisperx.load_model(model, device)
    
    # Create a temporary directory to store the ripped audio file
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            audio_rip_path = f'{tmpdir}/{os.path.basename(file)}.wav'
            rip_audio_file(file, audio_rip_path)
            # Perform the transcription
            result = transcribe(whisper_model, audio_rip_path, _logger)
            # Perform the alignment
            align_model, align_metadata = whisperx.load_align_model(
                'en', device)
            result_aligned = whisperx.align(
                result["segments"], align_model, align_metadata, audio_rip_path, device)
        except ffmpeg.Error as e:
            _logger.error(
                f'No English audio track found in {file}, error: {e.stderr}')
            raise ValueError(f'No English audio track found in {file}')
    
    # Extract forced subtitles if they exist
    forced_subs_path = None
    with tempfile.NamedTemporaryFile(suffix=".ass") as forced_subs_temp:
        if extract_forced_subtitles(file, forced_subs_temp.name):
            forced_subs_path = forced_subs_temp.name
            forced_subs_temp.flush()

    # Write the results to the output file
    if forced_subs_path:
        subs = merge_subtitles(result_aligned["segments"], forced_subs_path)
        subs.save(output_path.as_posix())
    else:
        save_results(result_aligned, output_path)

    return f"Transcribed {file} to {output_path}"

