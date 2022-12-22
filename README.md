# Whisper gRPC Python Project

This is a gRPC Python project that can transcribe items located on the server. It currently implements the `LocalTranscribeAnimeDub` endpoint.

## Starting the Server

To start the server, run the following command:

<pre><div class="bg-black mb-4 rounded-md"><code class="!whitespace-pre-wrap hljs language-bash">python whisper/server.py
</code></div></div></pre>

By default, the server is quiet, but it takes the `-v` and `-vv` arguments to increase the verbosity of the output.

## Installing the Client

To install the client, you can use `pip` as follows:

<pre><div class="bg-black mb-4 rounded-md"><div class="flex items-center relative text-gray-200 bg-gray-800 px-4 py-2 text-xs font-sans"><div class="p-4 overflow-y-auto"><code class="!whitespace-pre-wrap hljs">pipenv install git+https://github.com/Juxsta/whisper_grpc.git#egg=whisper-grpc
</code></div></div></pre>


This will install the `whisper_pb2_grpc` module, which you can use to create a client stub and call the service's RPC methods.

Here is an example of how to use the client code:

<pre><div class="p-4 overflow-y-auto"><code class="!whitespace-pre-wrap hljs language-python">import whisper_pb2_grpc

# Create a channel to the server
channel = grpc.insecure_channel('localhost:50051')

# Create a client stub
stub = whisper_pb2_grpc.WhisperStub(channel)

# Call the service's RPC method
response = stub.Transcribe(request)</code></div></div></pre>
