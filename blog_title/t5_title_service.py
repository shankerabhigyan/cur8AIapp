# blog/services/t5_title_service.py
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import logging

logger = logging.getLogger(__name__)

class T5TitleGenerator:
    def __init__(self):
        self.model_name = "fabiochiu/t5-base-medium-title-generation"
        try:
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            if torch.cuda.is_available():
                self.model = self.model.cuda()
        except Exception as e:
            logger.error(f"Error initializing T5 model: {str(e)}")
            raise

    def generate_titles(self, content: str, max_titles: int = 3) -> list:
        try:
            # Prepare input
            input_text = f"generate title: {content[:512]}"  # Limit content length
            inputs = self.tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
            
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}

            outputs = self.model.generate(
                **inputs,
                max_length=64,
                num_return_sequences=max_titles,
                num_beams=max_titles * 2,
                no_repeat_ngram_size=2,
                diversity_penalty=0.8,
                temperature=0.7
            )

            titles = []
            for output in outputs:
                title = self.tokenizer.decode(output, skip_special_tokens=True)
                titles.append({
                    'title': title,
                })

            return titles

        except Exception as e:
            logger.error(f"Error generating titles with T5: {str(e)}")
            raise