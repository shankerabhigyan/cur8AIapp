# transcription/services.py
import requests
from django.conf import settings
import time

class AssemblyAIService:
    def __init__(self):
        self.api_key = settings.ASSEMBLY_AI_API_KEY
        self.base_url = "https://api.assemblyai.com/v2"
        self.headers = {
            "authorization": self.api_key,
            "content-type": "application/json"
        }

    def upload_file(self, audio_file):
        """Upload a file to AssemblyAI"""
        upload_url = f"{self.base_url}/upload"
        
        def read_file_chunks(file_object, chunk_size=5242880):
            while True:
                data = file_object.read(chunk_size)
                if not data:
                    break
                yield data

        upload_response = requests.post(
            upload_url,
            headers=self.headers,
            data=read_file_chunks(audio_file)
        )
        
        return upload_response.json()["upload_url"]

    def create_transcript(self, audio_url, speaker_detection=True):
        """Create a transcript with speaker detection"""
        transcript_endpoint = f"{self.base_url}/transcript"
        
        data = {
            "audio_url": audio_url,
            "speaker_labels": speaker_detection
        }
        
        response = requests.post(
            transcript_endpoint,
            json=data,
            headers=self.headers
        )
        
        return response.json()

    def get_transcript(self, transcript_id):
        """Get the transcript result"""
        endpoint = f"{self.base_url}/transcript/{transcript_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()