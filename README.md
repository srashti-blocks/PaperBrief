# PaperBrief: LLM Research Summarizer

Paste an abstract or a section of a research paper and get a structured summary: key findings, methods, limitations and keywords. The LLM output is validated against a schema before it reaches the user.

**Live demo:** https://paperbrief.onrender.com
**API docs (Swagger):** https://paperbrief.onrender.com/docs

> The demo runs on a free Render instance. The first request after idle can take 30-60 seconds while it wakes up. History is shared between visitors and resets on redeploys, so please don't paste sensitive text.

<!-- Add a screenshot or GIF: save it as docs/screenshot.png and uncomment the next line -->
<!-- ![PaperBrief screenshot](docs/screenshot.png) -->

## Features

- **Structured output:** every LLM response is validated against a Pydantic schema, so malformed output never reaches the user.
- **Automatic retries:** failed calls (bad JSON, timeouts, API errors) are retried up to 3 times with exponential backoff.
- **Model fallback:** if a Gemini model is retired, rate-limited or overloaded, the next model in the configured list is tried.
- **Run logging and reliability stats:** every run is stored with status, attempts, latency and error. `GET /api/stats` reports success, failure and retry-recovery counts.
- **Abuse protection:** per-IP rate limiting (5 summaries per minute) and a system-prompt guard against prompt injection.
- **Optional webhook:** set `WEBHOOK_URL` to notify an external automation (n8n, Make, etc.) whenever a summary is created.
- **Full CRUD REST API** backed by SQLite, with a vanilla JavaScript frontend served by FastAPI itself.

## Tech stack

Python, FastAPI, Pydantic, SQLite, httpx, slowapi, Gemini API, vanilla JavaScript (Fetch API), pytest. Deployed on Render.

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/summaries` | Create a summary (200-20,000 characters of text) |
| GET | `/api/summaries` | List recent runs |
| GET | `/api/summaries/{id}` | Get one summary |
| DELETE | `/api/summaries/{id}` | Delete a summary |
| GET | `/api/stats` | Success, failure and retry-recovery counts |

Example:

```bash
curl -X POST http://localhost:8000/api/summaries \
  -H "Content-Type: application/json" \
  -d '{"text": "<at least 200 characters of paper text>"}'
```

## Run locally

```bash
git clone https://github.com/srashti-blocks/PaperBrief.git
cd PaperBrief
python -m venv venv
venv\Scripts\activate          # Windows (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

Create a `.env` file (never commit it):

```
GEMINI_API_KEY=your-key-from-aistudio.google.com/apikey
```

Start the server:

```bash
uvicorn main:app --reload
```

Open http://localhost:8000. Without a `GEMINI_API_KEY` the app runs in demo mode and returns placeholder output.

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `GEMINI_API_KEY` | Yes (for real summaries) | Free key from Google AI Studio |
| `GEMINI_MODELS` | No | Comma-separated models, tried in order. Default: `gemini-3.5-flash,gemini-3.5-flash-lite,gemini-3.1-flash-lite` |
| `DB_PATH` | No | SQLite file path. Default: `paperbrief.db` |
| `WEBHOOK_URL` | No | URL notified after each successful summary |

## Tests

The Gemini call is mocked, so tests run without an API key and use a temporary database.

```bash
pip install -r requirements-dev.txt
pytest -v
```

Covered: input validation, successful summary, retry recovery after bad JSON, failure after max attempts, fenced-JSON handling, get/delete and stats.

## Design notes

- **Why validate and retry?** LLMs sometimes return invalid JSON or miss required fields. Validation plus retries turns an unreliable model call into a dependable API endpoint.
- **Why log every run?** Latency, attempts and errors make reliability measurable instead of guessed.
- **Known limitations:** SQLite on a free host is not persistent, and history is not per-user. A planned next step is Postgres with user accounts.

## Project structure

```
PaperBrief/
├── main.py                 # FastAPI app, routes, LLM and DB logic
├── static/index.html       # Frontend (HTML, CSS, JavaScript)
├── test_main.py            # pytest suite
├── conftest.py             # temp DB and rate-limit setup for tests
├── requirements.txt
├── requirements-dev.txt
└── pytest.ini
```