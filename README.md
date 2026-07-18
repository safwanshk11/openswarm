# HERMES

The Inbox That Runs Itself is a demo application for an AI-powered customer support inbox. It simulates a modern support workflow where incoming tickets are automatically classified, replies are drafted from a knowledge base, and no-reply items are summarized into a digest for the support team.

## Why this project exists

Support teams often deal with a flood of repetitive requests, urgent blockers, and low-priority feedback all at once. This project demonstrates how AI can help by taking care of the first-pass triage and draft generation, allowing people to focus on the issues that need real attention.

## Project workflow

<img width="1600" height="900" alt="image" src="https://github.com/user-attachments/assets/75806350-4217-4904-9f63-8473e09d61f5" />

## Demo video

https://github.com/user-attachments/assets/acfcdddd-6ba0-4cc6-b516-587d6593e8a7

Note: our API key ran out during the demo.

## Screenshot

<img width="1710" height="956" alt="image" src="https://github.com/user-attachments/assets/948f27ab-178a-4b92-bc77-f6d77d593679" />

## What it does

- Presents a live inbox of demo support tickets
- Classifies tickets by intent and urgency
- Determines whether an individual reply is needed
- Drafts a response grounded in a local knowledge base
- Reviews the draft and produces a final response
- Bundles no-reply tickets into a daily digest summary
- Supports a voicemail demo flow that creates a new ticket automatically

## Tech stack

- Frontend: React, TypeScript, Vite
- Styling: Tailwind CSS
- Backend: Python, FastAPI
- AI integration: Gemini API
- Data: JSON ticket store and markdown knowledge base files

## Project structure

- `src/` – React frontend application
- `src/components/` – UI components for the inbox, tray, digest panel, and trace overlay
- `server.py` – FastAPI backend entry point
- `pipeline.py` – orchestration of the triage, specialist, reviewer, and digest flow
- `agents/` – agent modules and shared model client
- `kb/` – knowledge base articles used to ground generated replies
- `tickets.json` – sample ticket data used for the demo

## Prerequisites

Before running the app locally, make sure you have:

- Node.js and npm
- Python 3.10+
- A Gemini API key

## Setup

### 1. Install frontend dependencies

```bash
npm install
```

### 2. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn google-generativeai
```

### 3. Configure your Gemini API key

Create a file named `.env` in the project root with the following content:

```env
GEMINI_API_KEY="your_api_key_here"
```

You can also export it directly in your shell:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

## Running the app

### Start the backend

```bash
source .venv/bin/activate
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

### Start the frontend

In a second terminal:

```bash
npm run dev
```

Then open the local Vite URL shown in the terminal.

## How the demo works

1. The app loads the sample tickets from `tickets.json`.
2. The user processes the next ticket from the inbox.
3. The backend runs the triage agent to classify the request.
4. If a reply is needed, the specialist agent drafts a response using the knowledge base.
5. The reviewer agent checks the draft and produces a final version.
6. If no reply is needed, the ticket is grouped into the digest view.

## Notes about the AI layer

The demo uses Gemini for agent responses. Because free-tier quotas can be limited, the app includes a graceful fallback path so the demo can continue even if the API temporarily rejects requests. In that fallback mode, the app still shows a realistic demo response instead of crashing.

## Future improvements

Possible enhancements for the project include:

- Persistent storage instead of in-memory state
- Real authentication and user accounts
- A real database for tickets and reply history
- Better prompt tuning and structured output validation
- Deployment to a hosted environment with a production-grade backend

## License

This project is intended for demo and educational purposes.
