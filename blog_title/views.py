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
from openai import OpenAI

logger = logging.getLogger(__name__)

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

    def _generate_titles_with_openai(self, content: str, api_key: str, style: str = 'descriptive') -> list:
        """Generate titles using OpenAI API"""
        try:
            logger.info(f"Generating titles for content length: {len(content)}, style: {style}")
            
            client = OpenAI(api_key=api_key)
            
            base_prompt = f"""Generate ONLY ONE unique and engaging blog post title for the following content. 
Content: {content[:1000]}...

Requirements:
- Title should be clear and concise
- Maximum length of 60 characters
- Should focus on value proposition, catchiness & SEO optimization
Style :
"""
            
            style_prompts = [
                "descriptive: Generate a straightforward, descriptive title that clearly state the main topic.",
                "question: Generate a title in the form of intriguing question that provoke curiosity.",
                "action: Generate a action-oriented title that start with verbs and emphasize what readers will learn or achieve."
            ]
            
            # prompt = base_prompt + "\n" + style_prompts.get(style, style_prompts['descriptive'])

            prompts = []
            for style_prompt in style_prompts:
                prompts.append(base_prompt + "\n" + style_prompt)
            
            # response = client.chat.completions.create(
            #     model="gpt-4o",
            #     messages=[
            #         {"role": "system", "content": "You are a professional blog title generator."},
            #         {"role": "user", "content": prompt}
            #     ],
            #     temperature=0.7,
            #     max_tokens=150,
            #     n=1
            # )

            responses = []

            for prompt in prompts:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a professional blog title generator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150,
                    n=1
                )
                responses.append(response)

            titles = []
            for response in responses:
                for choice in response.choices:
                    title = choice.message.content.strip()
                    # Remove numbered bullets if present
                    title = title.split('. ', 1)[-1] if '. ' in title else title
                    titles.append({
                        'title': title,
                        'confidence_score': choice.finish_reason == 'stop' and 0.85 or 0.7
                    })

            logger.info(f"Successfully generated {len(titles)} titles")
            return titles
            
        except Exception as e:
            logger.error(f"Error in _generate_titles_with_openai: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    @action(detail=False, methods=['post'])
    def generate_titles(self, request):
        try:
            logger.info("Received title generation request")
            logger.info(f"Request data: {request.data}")
            
            serializer = TitleGenerationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            titles = self._generate_titles_with_openai(
                content=serializer.validated_data['content'],
                api_key=serializer.validated_data['openai_key'],
                style=serializer.validated_data['style']
            )
            
            blog_post = BlogPost.objects.create(
                title="Temporary Title",
                content=serializer.validated_data['content']
            )
            
            generated_titles = []
            for title_data in titles:
                generated_title = GeneratedTitle.objects.create(
                    blog_post=blog_post,
                    title=title_data['title'],
                    confidence_score=title_data['confidence_score']
                )
                generated_titles.append(generated_title)
            
            response_data = {
                'blog_post_id': blog_post.id,
                'titles': GeneratedTitleSerializer(generated_titles, many=True).data
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