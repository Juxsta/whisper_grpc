FROM anibali/pytorch:1.13.0-cuda11.8-ubuntu22.04


ENV VERBOSE=true
ENV VERY_VERBOSE=false
ENV PLEX_URL=http://localhost:32400
ENV PLEX_TOKEN=your-plex-token
ENV MAX_CONCURRENT_TRANSCRIBES=4
ENV HOST=127.0.0.1
ENV PORT=50051
# Copy the Pipfile and Pipfile.lock into the container
RUN apt-get update && apt-get install -y libmagic-dev ffmpeg
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy
# Copy the rest of the source code into the container
COPY whisper_grpc /app/whisper_grpc

# Set the working directory to the root of the project
WORKDIR /app

COPY . /app

RUN /usr/bin/yes | pip uninstall ffmpeg-python
RUN /usr/bin/yes | pip install ffmpeg-python
# Creates a non-root user and adds permission to access the /app folder
RUN adduser -u 1000 --disabled-password --gecos "" whisper_grpc && chown -R whisper_grpc /app
USER whisper_grpc

# Run the server when the container starts
CMD ["python", "whisper_grpc/server.py"]
