import logging, magic, tempfile, whisper, os, ffmpeg
from whisper.utils import write_srt
from pathlib import Path

def transcribe_file(file, model, logging_level=logging.WARNING):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging_level)
    output_path = Path(file).with_suffix('.en.srt')
    if  output_path.exists(): 
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
                output_file = str(Path(tmpdir) / os.path.basename(file).with_suffix('.wav'))
                transcribe_audio_file(file, output_file)
                result = whisper.transcribe(
                    model, output_file, beam_size=5, best_of=5, verbose=logger.getEffectiveLevel() <= logging.DEBUG,
                    language="en")
            except ffmpeg.Error as e:
                logger.error(f'No English audio track found in {file}, error: {e.stderr}')
                raise ValueError(f'No English audio track found in {file}')
        save_results(result, output_path)
        return f"Transcribed {file} to {output_path}"
    else:
        logger.error(f'Unsupported file type: {file_type}')
        raise ValueError(f'Unsupported file type: {file_type}')

def transcribe_audio_file(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .audio_filter("-map 0:a:m:language:eng")
        .audio_codec("pcm_s16le")
        .output(output_file)
        .run()
    )

def save_results(result, output_path):
    with open(output_path, "w", encoding="utf-8") as srt:
        write_srt(result["segments"], file=srt)

