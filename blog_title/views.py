from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
import logging
import traceback
from .models import BlogPost, GeneratedTitle
from .serializers import (
    BlogPostSerializer, 
    GeneratedTitleSerializer,
    TitleGenerationRequestSerializer
)

from .t5_title_service import T5TitleGenerator
from openai import OpenAI

logger = logging.getLogger(__name__)

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

    def _generate_titles_with_openai(self, content: str, api_key: str, style: str = 'descriptive') -> list:
        """Generate blog-post titles using OpenAI API"""
        try:
            logger.info(f"Generating titles for content length: {len(content)}, style: {style}")
            
            # get api key from settings
            from django.conf import settings
            if not hasattr(settings, 'OPENAI_API_KEY') or settings.OPENAI_API_KEY=="":
                raise ValidationError("OpenAI API key not found in settings")
                
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            base_prompt = f"""Generate ONE unique and engaging blog post title for the following content. 
    Content: {content[:1000]}...

    Requirements:
    - Title should be clear and concise
    - Maximum length of 60 characters
    - Should focus on value proposition, catchiness & SEO optimization
    Style :
    """
            
            style_prompts = {
                "descriptive": "Generate straightforward, descriptive titles that clearly state the main topic.",
                "question" : "Generate titles in the form of intriguing question that provoke curiosity.",
                "action" : "Generate action-oriented titles that start with verbs and emphasize what readers will learn or achieve."
            }
            
            # Create three separate prompts for each style
            titles = []
            for style_name, style_prompt in style_prompts.items():
                prompt = base_prompt + "\n" + style_prompt
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a professional blog title generator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150,
                    n=1  # One title per style
                )
                
                # Extract title from response
                title = response.choices[0].message.content.strip()
                titles.append({
                    'title': title
                })

            logger.info(f"Successfully generated {len(titles)} titles")
            return titles
            
        except Exception as e:
            logger.error(f"Error in _generate_titles_with_openai: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _generate_titles_with_t5(self, content: str, max_titles: int = 3) -> list:
        """Generate titles using T5 model"""
        try:
            generator = T5TitleGenerator()
            return generator.generate_titles(content, max_titles)
        except Exception as e:
            logger.error(f"Error in _generate_titles_with_t5: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    @action(detail=False, methods=['post'])
    def generate_titles(self, request):
        try:
            logger.info("Received title generation request")
            
            serializer = TitleGenerationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            model_choice = serializer.validated_data.get('model_choice', 'gpt')
            
            if model_choice == 'gpt':
                titles = self._generate_titles_with_openai(
                    content=serializer.validated_data['content'],
                    style=serializer.validated_data.get('style', 'descriptive')
                )
            else:  # using t5
                titles = self._generate_titles_with_t5(
                    content=serializer.validated_data['content'],
                    max_titles=serializer.validated_data.get('max_titles', 3)
                )
            
            response_data = {
                'titles': [
                    {
                        'title': title['title']
                    } 
                    for title in titles
                ]
            }
            
            logger.info(f"Successfully generated titles. Response: {response_data}")
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error in generate_titles: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {'error': f"Failed to generate titles: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )