# Cur8.ai Assignment - WebApp endpoints for Audio Transcription+ Diarization and Blog Title Generation
This Readme guides you through the step-by-step setup and testing of endpoints.

## Overview

## Setup
- Pull the repository and navigate to the project directory.
- Install the required packages using the following command:
```bash
pip install -r requirements.txt
```
- This project uses OpenAI API(optional) and AssemblyAI APIs to function, the API keys can be found in the `cur8app/settings.py` file @line 20. Please copy the API keys from the Google Document shared on my submission email and paste them in the file before proceeding.
- Run the following command to start the server:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
## Demo
The server will run on `http://127.0.0.1:8000/` by default, refer to call.ipynb in the project root to directly test the endpoints.
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
- Sample Response:
```json
{'job_id': 4,
 'text': "Smoke from hundreds of wildfires in Canada is triggering air quality alerts throughout the US Skylines from Maine to Maryland to Minnesota are gray and smoggy......"
 'utterances': [{'speaker': 'A',
   'text': "Smoke from hundreds of wildfires in Canada is triggering air quality alerts throughout the US Skylines from Maine to Maryland to Minnesota are gray and smoggy. And in some places, the air quality warnings include the warning to stay inside. We wanted to better understand what's happening here and why, so we called Peter DeCarlo, an associate professor in the Department of Environmental Health and Engineering at Johns Hopkins University. Good morning, Professor.",
   'start': 240,
   'end': 26780},
  {'speaker': 'B', 'text': 'Good morning.', 'start': 27820, 'end': 28884}...]
}
```