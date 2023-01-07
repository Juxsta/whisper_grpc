import unittest

import whisper_grpc.service as service

class TestLocalTranscribeAnimeDub(unittest.TestCase):
    def test_local_transcribe_anime_dub(self):
        """WIP test for LocalTranscribeAnimeDub"""
        # Create an instance of the WhisperHandler class
        handler = service.WhisperHandler()
        # Create a mock request object
        request = service.LocalTranscribeAnimeDubRequest(
            model='en-US',
            title='My Anime',
            show='My Show',
            season=1,
            episode=1
        )
        # Create a mock response object
        expected_response = service.LocalTranscribeAnimeDubResponse(
            status='Success',
            message='Transcription complete'
        )
        # Call the LocalTranscribeAnimeDub method
        response = handler.LocalTranscribeAnimeDub(request)
        # Verify that the response is correct
        self.assertEqual(response, expected_response)

if __name__ == '__main__':
    unittest.main()