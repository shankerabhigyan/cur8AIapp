# Cur8.ai Assignment - WebApp endpoints for Audio Transcription+ Diarization and Blog Title Generation
This Readme guides you through the step-by-step setup and testing of endpoints.

## Overview

## Setup
- Pull the repository and navigate to the project directory.
- Create a virtual environment using the following command:
```bash
python3 -m venv envcur8
source envcur8/bin/activate
```
- Install the required packages using the following command:
```bash
pip install -r requirements.txt
```
**IMPORTANT**:
- This project uses OpenAI API(optional) and AssemblyAI APIs to function, the API keys can be found in the `cur8app/settings.py` file @line 20. Please copy the API keys from the Google Document shared on my submission email and paste them in the file before proceeding.

- Run the following command to start the server:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
## Demo
The server will run on `http://127.0.0.1:8000/` by default.
NOTE: refer to `call.ipynb` in the project root to find the demo of the endpoints and helper functions to test the endpoints.
### Audio Transcription + Diarization
- The endpoint for Audio Transcription + Diarization is `/api/v1/transcription/transcribe/` and it accepts a `POST` request with the following parameters:
    - `audio_file`: The audio file to be transcribed.
- Sample Request:
```python
import requests

url = "http://localhost:8000/api/v1/transcription/transcribe/"
files = {'audio_file': open('/home/shankerabhigyan/code/cur8labs/audios/20230607_me_canadian_wildfires.mp3', 'rb')}
response = requests.post(url, files=files)
response.json()
``` 
In `call.ipynb` replace my file path with the path to your audio file and run the cell to test the endpoint.
- Equivalent CURL Request:
```bash
curl -X POST "http://localhost:8000/api/v1/transcription/transcribe/" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "audio_file=@/home/shankerabhigyan/code/cur8labs/audios/20230607_me_canadian_wildfires.mp3"
```
Replace the file path associated with audio_file with the path to your audio file and run the command to test the endpoint.
- Sample Response:
```txt
{'job_id': 4,
 'text': "Smoke from hundreds of wildfires in Canada is triggering air quality alerts throughout the US Skylines from Maine to Maryland to Minnesota are gray and smoggy......"
 'utterances': [{'speaker': 'A',
   'text': "Smoke from hundreds of wildfires in Canada is triggering air quality alerts throughout the US Skylines from Maine to Maryland to Minnesota are gray and smoggy. And in some places, the air quality warnings include the warning to stay inside. We wanted to better understand what's happening here and why, so we called Peter DeCarlo, an associate professor in the Department of Environmental Health and Engineering at Johns Hopkins University. Good morning, Professor.",
   'start': 240,
   'end': 26780},
  {'speaker': 'B', 'text': 'Good morning.', 'start': 27820, 'end': 28884}...]
}
```

### Blog Title Generation
The application uses 1. Fine-tuned T5-Base model finetuned for title generation and 2. OpenAI's GPT-4o model. The user has can easily switch between the two models by changing the `model_choice` parameter in the request.
- Sample Request:
```python
import requests

def generate_blog_titles(content: str, model_choice:str, style: str = 'descriptive') -> dict:
    url = "http://localhost:8000/blog_title/posts/generate_titles/"

    data = {
        "content": content,
        "model_choice": model_choice,
        "style": "descriptive",
        "max_titles": 3
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        return None
    
content = """
    Artificial Intelligence is transforming the way we work and live. From chatbots to 
    autonomous vehicles, AI technologies are becoming increasingly integrated into our 
    daily lives. This post explores the current state of AI technology, its applications
    across different industries, and what the future might hold for this rapidly 
    evolving field.
"""

model_choice = "gpt" # alternative : t5-finetuned for title generation (local model)
style = "descriptive" # alternative : "creative" are the other 2 options currently hardcoded while prompting
result = generate_blog_titles(content, model_choice)
print(result)
```
- Equivalent CURL Request:
```bash
curl -X POST "http://localhost:8000/blog_title/posts/generate_titles/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"content\": \"Artificial Intelligence is transforming the way we work and live. From chatbots to autonomous vehicles, AI technologies are becoming increasingly integrated into our daily lives. This post explores the current state of AI technology, its applications across different industries, and what the future might hold for this rapidly evolving field.\", \"model_choice\": \"gpt\", \"style\": \"descriptive\", \"max_titles\": 3}"
```
- Sample Response:
```txt
{'titles': [{'title': '"AI Revolution: Transforming Industries and Daily Life"'},
  {'title': '"How Is AI Revolutionizing Our Daily Lives and Industries?"'},
  {'title': 'Discover How AI is Revolutionizing Work and Life Today'}]}
```

## Note
- In case of any connection timeouts while testing the endpoints in the notebook, please wait for a few seconds and try again.
- 