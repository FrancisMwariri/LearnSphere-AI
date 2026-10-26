# LearnSphere AI

LearnSphere AI is an AI-powered virtual teacher. This repository contains a
React + Vite frontend and a Python + FastAPI backend. AI integrations are not
configured yet.

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
