# PaperBrief

A FastAPI + SQLite + LLM app that turns pasted research text into a validated, structured summary: title, summary, key findings, methods, limitations, and keywords.

## Features
- **REST API:** `POST /api/summaries`, `GET /api/summaries`, `GET /api/summaries/{id}`, `DELETE /api/summaries/{id}`, and `GET /api/stats`. Interactive docs at `/docs`.
- **Validated LLM output:** the model is prompted to return strict JSON, which is parsed and checked against a Pydantic schema (1-6 findings, 1-8 keywords, and so on).
- **Failure handling:** up to 3 attempts per request, with a short backoff between them. Malformed or truncated JSON, timeouts, and temporary API errors (such as 503 "high demand") trigger a retry instead of an immediate failure.
- **Run logging:** every run, successful or failed, is stored in SQLite with input size, attempt count, latency, and the error message if it failed.
- **Observability:** `/api/stats` reports total runs, successes, failures, average latency, and how many runs succeeded only after a retry.
- **Prompt-injection guard:** the system prompt tells the model to treat pasted text strictly as data.
- **Optional webhook:** set `WEBHOOK_URL` (for example an n8n or Make webhook) and each new summary fires a `summary.created` event. Webhook failures never break the request.
- **Frontend:** a single vanilla JS page with no build step.
- **Demo mode:** with no API key set, the app returns placeholder output so the UI can be tested.

## Run locally

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file (UTF-8, no quotes, no spaces around `=`):

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash
```

Get a free key at https://aistudio.google.com/apikey. Then start the server:

```bash
uvicorn main:app --reload
```

Open http://127.0.0.1:8000 (API docs at http://127.0.0.1:8000/docs).

Or set the variables in your shell instead of using `.env`:

```powershell
$env:GEMINI_API_KEY="your_key_here"    # PowerShell
$env:GEMINI_MODEL="gemini-3.5-flash"
```

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `GEMINI_API_KEY` | Enables real summaries (without it, demo mode runs) | none |
| `GEMINI_MODEL` | Gemini model name | `gemini-3.5-flash` |
| `DB_PATH` | SQLite file location | `paperbrief.db` |
| `WEBHOOK_URL` | Optional webhook called on each new summary | none |

Gemini model names are retired regularly. If you get a 404, list the models your key can use and update `GEMINI_MODEL`:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"
```

Lite models (for example `gemini-3.5-flash-lite`) respond faster and are enough for summarization. The alias `gemini-flash-latest` avoids breakage when a specific model is retired.

## Example

```bash
curl -X POST http://127.0.0.1:8000/api/summaries \
  -H "Content-Type: application/json" \
  -d '{"text": "<200 to 20,000 characters of paper text>"}'
```

The response includes the structured summary plus `id`, `attempts`, and `latency_ms`.

## Known limitations
- Input must be 200-20,000 characters.
- The API has no authentication, so don't expose it publicly with a paid key.
- Summary quality depends on the chosen model, and LLM latency varies from a few seconds to over 30 seconds.

## Deploy (Render)
1. New Web Service, then connect your GitHub repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add `GEMINI_API_KEY` and `GEMINI_MODEL` as environment variables.

Free-tier disks are ephemeral, so run history resets on every redeploy.

## Security
Never commit `.env` or API keys. This repo's `.gitignore` excludes `.env`, `venv/`, `paperbrief.db`, and `__pycache__/`.