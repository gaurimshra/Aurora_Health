# Aurora Health

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stack: FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)](#stack)
[![Stack: Next.js](https://img.shields.io/badge/frontend-Next.js-111111)](#stack)
[![Stack: Streamlit](https://img.shields.io/badge/studio-Streamlit-FF4B4B)](#stack)

Aurora Health is a multi-surface health and fitness product with:

- a FastAPI backend
- a Next.js web application
- a Streamlit studio/admin console

The project focuses on profile-driven plan generation, daily health tracking, semantic memory, weekly reports, and AI-assisted coaching.

## Product Surfaces

- `frontend/web`: the main user-facing Next.js application
- `frontend/studio`: a Streamlit studio/admin-style console
- `backend_service`: the FastAPI API and application logic

## Stack

Backend:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- Alembic
- OpenAI SDK
- Pinecone (optional)
- pytest

Frontend:

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Node.js 20.18.0+

Studio:

- Streamlit
- pandas
- httpx

## Repository Layout

```text
auroraHealth/
|- backend_service/
|  |- backend/
|  |  |- routes/      # API routes
|  |  |- services/    # business logic
|  |  |- models/      # Pydantic schemas
|  |  |- core/        # auth and OpenAI helpers
|  |  |- agents/      # domain heuristics/helpers
|  |- alembic/        # database migrations
|  |- tests/          # backend test suite
|  |- requirements.txt
|- frontend/
|  |- web/            # Next.js user-facing app
|  |- studio/         # Streamlit studio/admin UI
|- .env.example
|- run_backend.bat
|- run_web_app.bat
|- run_frontend.bat
|- run_all.bat
```

## Main Features

- User registration and login
- Profile setup with lifestyle and women-health context
- AI plan generation for workout, diet, and women-health guidance
- Workout, diet, progress, and streak logging
- Period tracking and cycle-aware recommendations
- Semantic memory storage and memory search
- Weekly report generation
- Aurora coaching and general chat

## Environment Variables

Create a root `.env` file for backend settings. Example:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CLERK_JWT_VERIFICATION_KEY=
```

For the Next.js app, use `frontend/web/.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
```

Do not commit real `.env` files or API keys.

## Local Setup

### 1. Backend

Create and activate a virtual environment, then install dependencies:

```powershell
cd backend_service
python -m venv ..\.venv
& ..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Or use the provided batch file from the repo root:

```bat
run_backend.bat
```

The backend runs on `http://127.0.0.1:8000`.

### 2. Next.js Web App

From the repo root:

```bat
run_web_app.bat
```

The web app runs on `http://127.0.0.1:3000`.

### 3. Streamlit Studio

From the repo root:

```bat
run_frontend.bat
```

Alias:

```bat
run_studio.bat
```

The studio app runs on `http://127.0.0.1:8501`.

The current Streamlit studio includes:

- login/signup-first entry flow
- persistent sidebar navigation
- top summary bar
- card-based dashboard and plan views
- local avatar rendering without external asset dependency

### 4. Start Everything

From the repo root:

```bat
run_all.bat
```

This starts:

- backend on `8000`
- web app on `3000`
- studio on `8501`

## Tests

Run backend tests with:

```powershell
cd backend_service
python -m pytest -q tests
```

## Notes

- The backend works without OpenAI credentials by using fallback responses.
- Pinecone is optional. If not configured, semantic memory search falls back to local similarity search.
- Clerk support is optional. The current app also supports local auth stored in SQLite.
- The Next.js app is the main end-user frontend. The Streamlit app is better treated as a studio/admin console.

## Deployment

Deploy the backend first, then point the web and Streamlit apps at the deployed backend URL.

Suggested order:

1. Deploy `backend_service`
2. Set `NEXT_PUBLIC_BACKEND_URL` for `frontend/web`
3. Set the Streamlit API base URL to the deployed backend
4. Deploy `frontend/web`
5. Deploy `frontend/studio`

See [DEPLOYMENT.md](DEPLOYMENT.md) for a production-oriented deployment checklist and service split.

## License

This repository includes the [LICENSE](LICENSE) file in the project root.
