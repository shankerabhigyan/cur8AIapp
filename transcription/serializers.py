# transcription/serializers.py
from rest_framework import serializers
from .models import TranscriptionJob

class TranscriptionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranscriptionJob
        fields = '__all__'