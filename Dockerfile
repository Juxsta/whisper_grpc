FROM python:3.8-bullseye

# Copy the Pipfile and Pipfile.lock into the container
RUN apt-get update && apt-get install -y libmagic-dev
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

# Copy the rest of the source code into the container
COPY whisper /app/whisper

# Set the working directory to the root of the project
WORKDIR /app

COPY . /app

# Creates a non-root user and adds permission to access the /app folder
RUN adduser -u 1000 --disabled-password --gecos "" whisper && chown -R whisper /app
USER whisper

# Run the server when the container starts
CMD ["python", "whisper/server.py", "-vv"]
