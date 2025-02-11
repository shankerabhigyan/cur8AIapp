from typing import List, Dict
import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class TitleGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    def _create_prompt(self, content: str, style: str) -> str:
        base_prompt = f"""Generate 3 unique and engaging blog post titles for the following content. 
Content: {content[:1000]}...

Requirements:
- Titles should be clear and concise
- Maximum length of 60 characters
- Should capture the main topic and value proposition
"""
        
        style_prompts = {
            'descriptive': "Generate straightforward, descriptive titles that clearly state the main topic.",
            'question': "Generate titles in the form of intriguing questions that provoke curiosity.",
            'action': "Generate action-oriented titles that start with verbs and emphasize what readers will learn or achieve."
        }
        
        return base_prompt + "\n" + style_prompts.get(style, style_prompts['descriptive'])

    async def generate_titles(
        self, 
        content: str, 
        style: str = 'descriptive',
        max_titles: int = 3
    ) -> List[Dict[str, float]]:
        try:
            prompt = self._create_prompt(content, style)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional blog title generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150,
                n=max_titles
            )

            titles = []
            for choice in response.choices:
                title = choice.message.content.strip()
                # Remove numbered bullets if present
                title = title.split('. ', 1)[-1] if '. ' in title else title
                titles.append({
                    'title': title,
                    'confidence_score': choice.finish_reason == 'stop' and 0.85 or 0.7
                })

            return titles[:max_titles]

        except Exception as e:
            logger.error(f"Error generating titles: {str(e)}")
            raise ValueError(f"Failed to generate titles: {str(e)}")