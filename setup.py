from setuptools import setup, find_packages

setup(
    name='whisper-server',
    version='1.0.0',
    description='A server for the whisper project',
    packages=find_packages(),
    install_requires=[
        'grpcio',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2'
    ]
)
