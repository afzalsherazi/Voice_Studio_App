# AI Voice Studio

A professional Streamlit-based AI Text-to-Speech application powered by
Google Gemini TTS.

The application provides a modern dark AI SaaS interface for converting
text into natural-sounding speech.

## Features

- Google Gemini TTS
- Gemini 3.1 Flash TTS support
- Gemini 2.5 Flash TTS alternative
- Multiple Gemini voices
- Natural-language speaking styles
- Custom speaking instructions
- Speed control
- Application-level voice consistency control
- Application-level voice character control
- Style intensity control
- Character counter
- Word counter
- WAV audio output
- WAV download
- Browser TTS fallback
- Session-based generation history
- Clear history
- Responsive Streamlit layout
- Streamlit Secrets support
- No database
- No Docker
- No terminal required for deployment

## Technology

- Python
- Streamlit
- Google GenAI Python SDK
- Google Gemini TTS
- Browser SpeechSynthesis API
- Python standard-library WAV processing

## Architecture

The application follows this flow:

User text
→ Streamlit interface
→ Gemini TTS
→ PCM audio
→ WAV conversion
→ Streamlit audio player
→ WAV download

If Gemini TTS is unavailable, Browser TTS can be used as a free fallback.

## Important

This application does NOT use:

- ElevenLabs
- ElevenLabs API
- ElevenLabs voice cloning
- proprietary voices
- proprietary backend code
- proprietary source code

The interface is an original implementation inspired by the general
experience of modern AI voice-generation applications.

## Gemini TTS Model

The default model is:

gemini-3.1-flash-tts-preview

The application also provides:

gemini-2.5-flash-preview-tts

The model is stored as a configurable constant in `app.py`.

If Google changes the model name, update:

DEFAULT_MODEL

inside `app.py`.

## Gemini API Key

You need a Gemini API key.

Create one through Google AI Studio.

After creating the key, do NOT put it inside:

- app.py
- README.md
- GitHub
- screenshots
- public files

For Streamlit Community Cloud, add it through the application's Secrets
settings.

Use:

GEMINI_API_KEY = "YOUR_API_KEY"

## Project Structure

The repository contains:

app.py
requirements.txt
README.md
.gitignore

No other files are required.

## GitHub Deployment

### Step 1 — Create GitHub repository

1. Sign in to GitHub.
2. Click the "+" button in the upper-right corner.
3. Select "New repository".
4. Enter a repository name, for example:

AI-Voice-Studio

5. Choose Public if you want a simple public deployment.
6. Do not add unnecessary files.
7. Click "Create repository".

### Step 2 — Upload app.py

Inside your repository:

1. Click "Add file".
2. Select "Create new file".
3. Enter:

app.py

4. Paste the complete application code.
5. Click "Commit changes".

### Step 3 — Upload requirements.txt

1. Click "Add file".
2. Select "Create new file".
3. Name it:

requirements.txt

4. Paste the requirements.
5. Click "Commit changes".

### Step 4 — Upload README.md

1. Click "Add file".
2. Select "Create new file".
3. Name it:

README.md

4. Paste this README.
5. Click "Commit changes".

### Step 5 — Upload .gitignore

1. Click "Add file".
2. Select "Create new file".
3. Name it:

.gitignore

4. Paste the .gitignore contents.
5. Click "Commit changes".

## Streamlit Community Cloud

Open:

https://share.streamlit.io/

Sign in with your GitHub account.

Connect GitHub if requested.

Then:

1. Click "Create app".
2. Select "Yup, I have an app".
3. Select your GitHub repository.
4. Select the `main` branch.
5. Set the main file to:

app.py

6. Open "Advanced settings".
7. Add the Gemini API key under Secrets.
8. Save the settings.
9. Click Deploy.

## Streamlit Secret

The secret should look like:

GEMINI_API_KEY = "YOUR_REAL_GEMINI_API_KEY"

Do not add:

```text
GEMINI_API_KEY=...
