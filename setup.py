from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name="whisper-grpc",
    version="0.1.0",
    author="John Doe",
    author_email="john.doe@example.com",
    description="A gRPC Python project for transcribing audio",
    long_description_content_type="text/markdown",
    url="https://github.com/johndoe/whisper-grpc",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "grpcio",
        "grpcio-tools"
    ],
    package_data={
        "whisper": [
            "whisper/proto/*.proto",
            "whisper/proto/*.py"
        ]
    },
)
