# Deployment Guide

This repository has three runtime surfaces:

- FastAPI backend
- Next.js web app
- Streamlit studio

For most public deployments, the recommended approach is:

- deploy the FastAPI backend as one service
- deploy the Next.js web app as one service
- keep the Streamlit studio private or deploy it separately only if needed

## Recommended Production Shape

### Backend

Deploy the backend from `backend_service/` to a Python host that supports:

- Python 3.11+
- environment variables
- persistent filesystem only if you keep SQLite

Recommended production command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

If you expect real public traffic, consider moving from SQLite to a managed database. SQLite is acceptable for demos, private usage, and light internal testing, but it is not the strongest multi-user production choice.

### Web App

Deploy the Next.js app from `frontend/web/`.

Required environment variables:

```env
NEXT_PUBLIC_BACKEND_URL=https://your-backend-domain
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
```

Build command:

```bash
npm run build
```

Start command:

```bash
npm run start
```

### Streamlit Studio

The Streamlit app lives in `frontend/studio/app.py`.

It is better treated as:

- an internal operator tool
- a demo workspace
- a private admin console

If you deploy it publicly, protect it behind authentication or a private network.

## Backend Environment Variables

Use the root `.env` shape from `.env.example`:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
CORS_ORIGINS=https://your-web-domain
CLERK_JWT_VERIFICATION_KEY=
```

## Production Checklist

- Set `NEXT_PUBLIC_BACKEND_URL` to the deployed backend URL.
- Set `CORS_ORIGINS` to your deployed frontend origin.
- Keep `.env` and `.env.local` out of git.
- Confirm the backend works without OpenAI/Pinecone if those keys are intentionally omitted.
- Decide whether auth is local-only or Clerk-enabled in production.
- Do not expose the Streamlit studio publicly unless you intend to support it as a separate product surface.
- Move off SQLite if you need stronger production durability and concurrent write handling.

## Smoke Test After Deployment

Backend:

- open `/`
- verify the health response is returned
- test `/auth/register`, `/auth/login`, and `/auth/me`

Web app:

- load the home page
- register/login
- save a profile
- generate a plan
- log workout, diet, and progress entries
- verify weekly report and coach responses

Studio:

- confirm backend connectivity
- confirm sign-in works
- verify snapshot loading and export buttons
