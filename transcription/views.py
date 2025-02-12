# transcription/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TranscriptionJob
from .serializers import TranscriptionJobSerializer
import assemblyai as aai
from django.conf import settings
import tempfile

class TranscriptionViewSet(viewsets.ModelViewSet):
    queryset = TranscriptionJob.objects.all()
    serializer_class = TranscriptionJobSerializer

    @action(detail=False, methods=['POST'])
    def transcribe(self, request):
        if 'audio_file' not in request.FILES:
            return Response(
                {'error': 'No audio file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        audio_file = request.FILES['audio_file']
        
        # Initialize AssemblyAI
        aai.settings.api_key = settings.ASSEMBLY_AI_API_KEY
        
        # Create a temporary file to save the uploaded audio
        # with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        #     for chunk in audio_file.chunks():
        #         tmp_file.write(chunk)
        #     tmp_file_path = tmp_file.name

        try:
            # Configure transcription with speaker labels
            config = aai.TranscriptionConfig(speaker_labels=True)
            transcriber = aai.Transcriber()
            
            # Start transcription
            transcript = transcriber.transcribe(
                audio_file,
                config=config
            )

            # Format the response
            utterances = [
                {
                    "speaker": utterance.speaker,
                    "text": utterance.text,
                    "start": utterance.start,
                    "end": utterance.end
                }
                for utterance in transcript.utterances
            ]

            # Save to database
            job = TranscriptionJob.objects.create(
                audio_file=audio_file,
                status='COMPLETED',
                assembly_ai_id=transcript.id,
                result={
                    'text': transcript.text,
                    'utterances': utterances
                }
            )

            return Response({
                'job_id': job.id,
                'text': transcript.text,
                'utterances': utterances,
                'status': 'COMPLETED'
            })

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # finally:
        #     # Clean up the temporary file
        #     import os
        #     try:
        #         os.unlink(tmp_file_path)
        #     except:
        #         pass