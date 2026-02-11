from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
import datetime as dt, uuid, datetime as dt

from receipt_engine import build_receipt
from renderer import render_receipt_png, render_badge_png

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
RECEIPTS = DATA / "receipts"
IMAGES = DATA / "images"
BADGES = DATA / "badges"
WAITLIST = DATA / "waitlist.jsonl"
SUBSCRIBERS = DATA / "subscribers.jsonl"
RECEIPTS.mkdir(parents=True, exist_ok=True)
IMAGES.mkdir(parents=True, exist_ok=True)
BADGES.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Chambiar Receipt MVP")
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")

def _save_receipt(receipt: dict) -> str:
    rid = str(uuid.uuid4())[:8]
    receipt["receipt_id"] = rid
    (RECEIPTS / f"{rid}.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    render_receipt_png(receipt, str(IMAGES / f"{rid}.png"))
    render_badge_png(receipt, str(BADGES / f"{rid}.png"))
    return rid

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(str(BASE / "static" / "index.html"))

@app.post("/api/receipt-lite")
async def receipt_lite(request: Request):
    payload = await request.json()
    receipt = build_receipt(payload or {})
    rid = _save_receipt(receipt)
    top2 = sorted(receipt["signals"]["scores"].items(), key=lambda kv: kv[1], reverse=True)[:2]
    return {
        "receipt_id": rid,
        "receipt_url": f"/r/{rid}",
        "image_url": f"/i/{rid}.png",
        "badge_url": f"/b/{rid}.png",
        "house": receipt["house_key"],
        "variant": receipt["variant_key"],
        "top_areas": top2,
    }


async def _append_subscriber(payload: dict):
    email = (payload.get("email") or "").strip()
    if not email or "@" not in email:
        return JSONResponse({"ok": False, "error": "Valid email required."}, status_code=400)

    prefs = {
        "beta_tester": bool(payload.get("beta_tester")),
        "newsletter": bool(payload.get("newsletter")),
        "notify_launch": bool(payload.get("notify_launch")),
    }

    record = {
        "email": email,
        "created_at": dt.datetime.utcnow().isoformat() + "Z",
        "receipt_id": payload.get("receipt_id"),
        "house": payload.get("house"),
        "variant": payload.get("variant"),
        "top_areas": payload.get("top_areas"),
        "utm": payload.get("utm", {}),
        "prefs": prefs,
        "source": payload.get("source", "unknown"),
    }

    DATA.mkdir(parents=True, exist_ok=True)
    with SUBSCRIBERS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return JSONResponse({"ok": True})

@app.post("/api/subscribe")
async def subscribe(request: Request):
    payload = await request.json()
    payload = payload or {}
    return await _append_subscriber(payload)

@app.post("/api/waitlist")
async def waitlist(request: Request):
    # Backwards-compatible alias: treat as "notify_launch"
    payload = await request.json()
    payload = payload or {}
    payload.setdefault("notify_launch", True)
    payload.setdefault("source", "waitlist_alias")
    return await _append_subscriber(payload)

@app.get("/r/{rid}", response_class=HTMLResponse)
def receipt_page(rid: str):
    p = RECEIPTS / f"{rid}.json"
    if not p.exists():
        return HTMLResponse("Not found", status_code=404)
    receipt = json.loads(p.read_text(encoding="utf-8"))
    top2 = sorted(receipt["signals"]["scores"].items(), key=lambda kv: kv[1], reverse=True)[:2]

    cards_html = "".join([
        f"<div class='mini'><h4>{c['title']}</h4>"
        f"<div><b>Signal:</b> {c['signal']}</div>"
        f"<div><b>Maria does:</b> {c['maria']}</div>"
        f"<div><b>Outcome:</b> {c['outcome']}</div></div>"
        for c in receipt.get("cheat_sheet", [])
    ])

    caption_plain = (
        f"I’m {receipt.get('variant_name','')} (Work Mode: {receipt.get('house_name','')}).\n\n"
        f"{receipt.get('variant_means','')}\n\n"
        f"Fastest win: {receipt.get('fastest_win','')}\n\n"
        f"Want your own share-safe archetype + Work Week Receipt? Comment ‘RECEIPT’ and I’ll send the link."
    )

    html = f"""
<!doctype html>
<html>
<head>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Work Mode Quiz Result + Receipt</title>
  <meta property="og:title" content="My Work Week Work Mode: {variant_name}"/>
  <meta property="og:description" content="60-second quiz • share-safe • get your badge + receipt"/>
  <meta property="og:image" content="{badge_abs}"/>
  <meta property="og:url" content="{page_abs}"/>
  <meta name="twitter:card" content="summary_large_image"/>

  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; background:#fafafa; margin:0; }}
    .wrap {{ max-width: 920px; margin: 0 auto; padding: 24px; }}
    .card {{ background:#fff; border:1px solid #e6e6e6; border-radius: 18px; padding: 18px; }}
    img {{ width:100%; height:auto; border-radius: 12px; border:1px solid #eee; }}
    .row {{ display:flex; gap:12px; flex-wrap:wrap; margin-top: 12px; }}
    button, input, textarea {{ font-size:16px; padding:12px 14px; border-radius:12px; border:1px solid #ddd; }}
    button {{ background:#111; color:#fff; border:none; cursor:pointer; }}
    .muted {{ color:#666; font-size: 14px; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin-top: 14px; }}
    .mini {{ border:1px solid #eee; border-radius:14px; padding: 12px; }}
    .mini h4 {{ margin:0 0 6px 0; font-size:14px; }}
    .mini div {{ font-size:13px; color:#333; margin-bottom: 6px; }}
    .two {{ display:grid; grid-template-columns: 1fr; gap: 12px; }}
    @media (min-width: 860px) {{ .two {{ grid-template-columns: 1fr 1fr; }} }}
    textarea {{ width: 100%; min-height: 120px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h2 style="margin:0 0 10px 0;">Your Work Mode Quiz Result + Receipt</h2>
      <div class="muted">Share-safe. No message titles/subjects/names. Ranges + normalized labels only.</div>

      <div class="two" style="margin-top:12px;">
        <div>
          <h3 style="margin:0 0 8px 0;">LinkedIn Badge (best for posting)</h3>
          <img src="/b/{rid}.png" alt="Badge image"/>
          <div class="row">
            <a href="/b/{rid}.png" download><button>Download badge</button></a>
            <button onclick="navigator.clipboard.writeText(document.getElementById('cap').value)">Copy LinkedIn caption</button>
          </div>
          <div style="height:10px;"></div>
          <textarea id="cap">{caption_plain}</textarea>
          <div class="muted" style="margin-top:8px;">Tip: post the badge + caption. Ask a question (e.g., “What’s your Work Mode?”).</div>
        </div>

        <div>
          <h3 style="margin:0 0 8px 0;">Full Receipt (proof + plan)</h3>
          <img src="/i/{rid}.png" alt="Receipt image"/>
          <div class="row">
            <a href="/i/{rid}.png" download><button>Download receipt</button></a>
            <button onclick="navigator.clipboard.writeText(window.location.href)">Copy link</button>
            <a href="/"><button style="background:#2b2b2b;">Make yours</button></a>
          </div>
        </div>
      </div>

      <div style="height:18px;"></div>
      <h3 style="margin:0 0 8px 0;">Stay close to the launch</h3>
      <div class="muted" style="margin-bottom:10px;">One email. Choose what you want. No spam.</div>
      <div class="row">
        <input id="email" placeholder="you@example.com" style="flex:1; min-width:240px;"/>
        <button onclick="signup()">Notify me at launch</button>
      </div>
      <div id="msg" class="muted" style="margin-top:8px;"></div>

      <div style="height:18px;"></div>
      <h3 style="margin:0 0 8px 0;">Full picture (what Maria could do)</h3>
      <div class="muted">Cheat sheet preview—based on other common patterns.</div>
      <div class="grid">{cards_html}</div>
    </div>
  </div>
<script>
async function signup() {{
  const email = document.getElementById('email').value;
  const res = await fetch('/api/subscribe', {{
    method:'POST',
    headers:{{'Content-Type':'application/json'}},
    body: JSON.stringify({{
      email,
      receipt_id: '{rid}',
      house: '{receipt.get("house_key","")}',
      variant: '{receipt.get("variant_key","")}',
      top_areas: {json.dumps(top2)}
    }})
  }});
  const data = await res.json();
  const msg = document.getElementById('msg');
  msg.textContent = data.ok ? "You’re on the list. We’ll email you at launch." : (data.error || "Something went wrong.");
}}
</script>
</body>
</html>
"""
    return HTMLResponse(html)

@app.get("/i/{rid}.png")
def receipt_image(rid: str):
    p = IMAGES / f"{rid}.png"
    if not p.exists():
        return JSONResponse({"error":"Not found"}, status_code=404)
    return FileResponse(str(p), media_type="image/png")

@app.get("/b/{rid}.png")
def badge_image(rid: str):
    p = BADGES / f"{rid}.png"
    if not p.exists():
        return JSONResponse({"error":"Not found"}, status_code=404)
    return FileResponse(str(p), media_type="image/png")
