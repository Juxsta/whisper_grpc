from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name="whisper_grpc",
    version="0.1.0",
    author="Juxsta",
    description="A gRPC Python project for transcribing audio",
    python_requires=">=3.8",
    long_description_content_type="text/markdown",
    url="https://github.com/Juxsta/whisper_grpc",
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
            "proto/*.proto",
            "proto/*.py"
        ]
    },
)
