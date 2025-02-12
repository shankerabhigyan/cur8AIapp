from rest_framework import serializers
from .models import BlogPost, GeneratedTitle

class GeneratedTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedTitle
        fields = ['id', 'title', 'confidence_score', 'created_at', 'selected']

class BlogPostSerializer(serializers.ModelSerializer):
    generated_titles = GeneratedTitleSerializer(many=True, read_only=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'generated_titles']

class TitleGenerationRequestSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)
    max_titles = serializers.IntegerField(default=3, min_value=1, max_value=5)
    style = serializers.ChoiceField(
        choices=['descriptive', 'question', 'action'],
        default='descriptive'
    )