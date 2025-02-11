# transcription/tasks.py
from celery import shared_task
from .models import TranscriptionJob
from .services import AssemblyAIService
import time

@shared_task
def process_transcription(job_id):
    job = TranscriptionJob.objects.get(id=job_id)
    service = AssemblyAIService()

    try:
        # Update status to processing
        job.status = 'PROCESSING'
        job.save()

        # Upload file to AssemblyAI
        with job.audio_file.open('rb') as audio_file:
            upload_url = service.upload_file(audio_file)

        # Create transcript
        transcript_response = service.create_transcript(upload_url)
        job.assembly_ai_id = transcript_response['id']
        job.save()

        # Poll for completion
        while True:
            result = service.get_transcript(job.assembly_ai_id)
            if result['status'] == 'completed':
                job.status = 'COMPLETED'
                job.result = result
                job.save()
                break
            elif result['status'] == 'error':
                job.status = 'FAILED'
                job.error_message = result.get('error', 'Unknown error')
                job.save()
                break
            time.sleep(5)

    except Exception as e:
        job.status = 'FAILED'
        job.error_message = str(e)
        job.save()