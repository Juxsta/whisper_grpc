.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/whisper_grpc.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/whisper_grpc
    .. image:: https://readthedocs.org/projects/whisper_grpc/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://whisper_grpc.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/whisper_grpc/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/whisper_grpc
    .. image:: https://img.shields.io/pypi/v/whisper_grpc.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/whisper_grpc/
    .. image:: https://img.shields.io/conda/vn/conda-forge/whisper_grpc.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/whisper_grpc
    .. image:: https://pepy.tech/badge/whisper_grpc/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/whisper_grpc
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/whisper_grpc

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

============
whisper_grpc
============


    Add a short description here!

How to compile protos
https://github.com/vmagamedov/grpclib
python3 -m grpc_tools.protoc -I. -I../third_party/googleapis --python_out=.  --experimental_allow_proto3_optional --grpclib_python_out=. --pyi_out=. --grpc-gateway_out=logtostderr=true:. whisper_grpc/proto/whisper.proto


.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.4. For details and usage
information on PyScaffold see https://pyscaffold.org/.
