FROM python:3.9.9-bullseye

ENV VERBOSE=true
ENV VERY_VERBOSE=false
ENV PLEX_URL=http://localhost:32400
ENV PLEX_TOKEN=your-plex-token
ENV MAX_CONCURRENT_TRANSCRIBES=4
ENV HOST=127.0.0.1
ENV PORT=50051
ENV HF_TOKEN=your-huggingface-token
# Copy the Pipfile and Pipfile.lock into the container
RUN apt-get update && apt-get install -y libmagic-dev ffmpeg libsndfile1
RUN python -m pip install --upgrade pip
COPY . .

RUN pip install .[server]


# Run the server when the container starts
CMD ["whisper_server"]
