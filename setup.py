from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name='whisper_grpc',
    version='0.1.0',    
    description='Whisper grpc server',
    url='https://github.com/juxsta/whisper_grpc',
    author='Juxsta',
    license='BSD 2-clause',
    packages=['whisper_grpc'],
    install_requires=[
        "grpcio",
        "grpcio-tools"
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
