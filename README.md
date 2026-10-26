# LearnSphere AI

LearnSphere AI is an AI-powered virtual teacher. This repository contains a
React + Vite frontend and a Python + FastAPI backend. The backend supports a
deterministic mock teaching provider by default and an optional OpenAI API
provider for model-generated lessons and answers.

## Prerequisites

- Node.js and npm
- Python 3.10 or newer

## Run the frontend

In Windows PowerShell, from the repository root:

```powershell
Set-Location .\frontend
npm.cmd install
npm.cmd run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173`).

## Run the backend

In a separate Windows PowerShell window, from the repository root:

```powershell
Set-Location .\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Check its health at
`http://127.0.0.1:8000/health`; interactive API documentation is available at
`http://127.0.0.1:8000/docs`.

### Backend tests

The backend requirements include the test dependencies. From the repository
root, run:

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m pytest
```

The versioned demonstration API is available under `/api/v1`. It returns
clearly labelled sample content. Local Vite CORS origins default to
`http://localhost:5173` and
`http://127.0.0.1:5173`. Override them with a comma-separated
`LEARNINGSPHERE_CORS_ORIGINS` environment variable when needed.

### AI teaching engine foundation

The provider-independent teaching engine uses a deterministic local mock by
default. The mock does not call an AI service, access the internet, or require
an API key. To enable model-generated lessons and answers, use the OpenAI API
provider. Model-generated content is not independently verified or researched;
the API does not provide citations. Content is validated against Pydantic
schemas; visualization events use enumerated event types and structured scalar
parameters. Lesson code snippets, when present, are content only and are never
executed by the backend.

From `backend/`, copy the safe placeholder configuration and edit the local
`.env` file with your own API key. Never put provider credentials in frontend
configuration or request bodies, and do not commit `.env`:

```powershell
Copy-Item .env.example .env
# Edit .env and set TEACHING_PROVIDER=openai and OPENAI_API_KEY to your key.
```

Set `TEACHING_PROVIDER=mock` to return to the no-network mock. The OpenAI
provider defaults to `https://api.openai.com/v1` and `gpt-4o-mini`; its
`OPENAI_BASE_URL` and `OPENAI_MODEL` values can be changed in backend `.env`
for an API-compatible endpoint that supports strict JSON Schema outputs.
Restart the backend after changing provider settings. Remote endpoints must use
HTTPS; HTTP is permitted only for loopback development endpoints.
Missing configuration, rate limits, timeouts, and provider failures return
sanitized HTTP errors; provider response bodies and credentials are not
included.

Generate a lesson for an arbitrary learner-selected topic:

```powershell
$lessonRequest = @{
    topic = "Fractions"
    subject = "mathematics"
    learner_level = "beginner"
    learning_objective = "Explain how equivalent fractions represent the same value"
    preferred_explanation_style = "visual examples"
} | ConvertTo-Json

$lesson = Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/api/v1/teaching/lessons" `
    -ContentType "application/json" `
    -Body $lessonRequest
$lesson | ConvertTo-Json -Depth 10
```

Ask a lesson-related question. Lesson context is optional:

```powershell
$questionRequest = @{
    topic = "Fractions"
    question = "How can I check whether two fractions are equivalent?"
    learner_level = "beginner"
    lesson_context = @{
        lesson_title = $lesson.title
        learning_objective = $lesson.objectives[0]
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/api/v1/teaching/questions" `
    -ContentType "application/json" `
    -Body $questionRequest
```

Both endpoints are documented in `/docs`. Invalid requests return HTTP 422;
invalid provider output and provider failures return sanitized HTTP errors.

Run the complete backend test suite from the repository root:

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m pytest
```
