import logging, magic, tempfile, whisper, os, ffmpeg
from whisper.utils import write_srt
from pathlib import Path

def transcribe_file(file, model, verbose):
    output_path = Path(file).with_suffix('.en.srt')
    if  output_path.exists(): 
        logging.debug(f'Skipping {file} - external subtitles already exist')
        return
    if not os.path.isfile(file):
        logging.debug(f'Skipping {file} - not a file')
        return
    file_type = magic.from_file(file, mime=True)
    if file_type.startswith('audio/') or file_type.startswith('video/'):
        logging.info(f'Transcribing {file}')
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                output_file = str(Path(tmpdir) / os.path.basename(file).with_suffix('.wav'))
                transcribe_audio_file(file, output_file)
                result = whisper.transcribe(
                    model, output_file, beam_size=5, best_of=5, verbose=verbose, language="en")
            except ffmpeg.Error as e:
                logging.error(f'No English audio track found in {file}, error: {e.stderr}')
                return
        save_results(result, output_path)
    else:
        logging.debug(f'Unsupported file type: {file_type}')

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

