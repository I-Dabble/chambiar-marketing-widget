# Work Week Archetype + Receipt MVP

Prototype:
- 60-second survey → **House + Variant** archetype
- Generates:
  - **LinkedIn Badge** image (identity-first): `/b/{id}.png`
  - **Work Week Receipt** image (proof + plan): `/i/{id}.png`
- Share page `/r/{id}` includes:
  - Badge download + caption box + “Copy LinkedIn caption”
  - Receipt download + share link
  - Email waitlist CTA (“Notify me at launch”)

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open: http://127.0.0.1:8000


## Subscriptions
- POST `/api/subscribe` stores one email + preferences to `data/subscribers.jsonl`.
- `/api/waitlist` remains as a backwards-compatible alias.
