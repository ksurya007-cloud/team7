# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a FastAPI + HTML/CSS/JavaScript learning assistant based on the supplied project document.

## Features

- Q&A
- Beginner-friendly topic explanations
- 3-question MCQ quiz generation
- Passage summarization
- Personalized beginner-to-advanced learning paths
- Responsive browser UI
- Gemini API key kept server-side in `.env`
- `/health` endpoint for setup checks

## Project structure

```text
EduGenie/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── modules/
│   ├── __init__.py
│   └── ai_service.py
├── templates/
│   └── index.html
└── static/
    ├── app.js
    └── style.css
```

## VS Code setup — Windows

Open the EduGenie folder in VS Code.

### 1. Create a virtual environment

```powershell
py -3.10 -m venv .venv
```

If `py` is unavailable:

```powershell
python -m venv .venv
```

### 2. Activate it

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Gemini

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace:

```text
GEMINI_API_KEY=PASTE_YOUR_KEY_HERE
```

with your real key.

Do not commit `.env` to Git.

### 5. Start the website

```powershell
uvicorn main:app --reload
```

Open:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

## Testing

1. Open the home page.
2. Select `Ask a Question`.
3. Enter: `Which is the largest ocean?`
4. Click `Generate Answer`.
5. Test `Explain a Topic` with `Pythagoras theorem`.
6. Test `Summarize` with a paragraph.
7. Test `Generate Quiz` with a lesson passage.
8. Test `Learning Path` with `SQL` and choose a level.

## API examples

### Q&A

POST `/qa`

```json
{
  "question": "What is photosynthesis?"
}
```

### Explain

POST `/explain`

```json
{
  "text": "Explain binary search"
}
```

### Quiz

POST `/quiz`

```json
{
  "text": "Binary search works on sorted data by repeatedly dividing the search interval."
}
```

### Summary

POST `/summarize`

```json
{
  "text": "Long educational passage..."
}
```

### Learning path

POST `/learn/recommendations`

```json
{
  "topic": "SQL",
  "level": "Beginner"
}
```

## Troubleshooting

### `ModuleNotFoundError`

Make sure the virtual environment is activated and run:

```powershell
pip install -r requirements.txt
```

### `Gemini is not configured`

Check `.env`, especially:

```text
GEMINI_API_KEY=...
```

Then restart Uvicorn.

### API key errors

Create/verify your Gemini API key in Google AI Studio and ensure the selected Gemini model is available to your account.

### Port already in use

```powershell
uvicorn main:app --reload --port 8001
```

Then open:

http://127.0.0.1:8001

## Design note

The supplied document names Gemini 1.5 Pro and LaMini-Flan-T5-783M. Model availability can change over time, so this implementation makes the Gemini model configurable through `GEMINI_MODEL` and defaults to `gemini-2.5-flash`. The explanation feature is kept as a dedicated `/explain` module/API but uses Gemini by default, avoiding a large local model download and making the project easier to run on a normal student laptop.
