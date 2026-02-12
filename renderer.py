from __future__ import annotations
from typing import Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math
import random

RECEIPT_W, RECEIPT_H = 1080, 1350
BADGE_W, BADGE_H = 1080, 1080

# "Chambiar.ai" visual theme translation:
# - High contrast, lots of whitespace, "invisible" UI
# - Subtle gradients + thin rules
# - Minimal patterns (no confetti). Small "orbit" dots instead.
# - Accent colors are muted (still distinct per House)

HOUSE_STYLE = {
    "CALENDAR": {"accent": (247, 147, 26),  "emoji": "🗓️", "label": "Calendar Load"},
    "CURRENT":  {"accent": (0, 171, 255),   "emoji": "🌊", "label": "Message Current"},
    "COUNCIL":  {"accent": (164, 98, 240),  "emoji": "🏛️", "label": "Decision Council"},
    "GLUE":     {"accent": (46, 200, 106),  "emoji": "🧩", "label": "Ops Glue"},
}

# Neutral system palette
INK = (14, 16, 20)          # near-black
MUTED = (92, 98, 112)       # body gray
HAIRLINE = (230, 233, 240)  # thin borders
PAPER = (252, 252, 253)     # warm white
PAPER_2 = (246, 248, 252)   # cool off-white

def _font(size: int, bold: bool=False):
    if bold:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()

def _wrap(draw, text, font, max_width):
    words = (text or "").split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def _rounded_rect(draw, xy, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(list(xy), radius=r, fill=fill, outline=outline, width=width)

def _linear_gradient(size: Tuple[int,int], c1: Tuple[int,int,int], c2: Tuple[int,int,int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", (w, h), c1)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h-1)
        r = int(c1[0]*(1-t) + c2[0]*t)
        g = int(c1[1]*(1-t) + c2[1]*t)
        b = int(c1[2]*(1-t) + c2[2]*t)
        d.line((0, y, w, y), fill=(r,g,b))
    return img

def _add_soft_noise(img: Image.Image, amount: int = 10) -> Image.Image:
    # Gentle texture so it doesn't look like a flat template.
    w, h = img.size
    noise = Image.new("L", (w, h), 128)
    px = noise.load()
    rng = random.Random(11)
    for y in range(h):
        for x in range(w):
            px[x, y] = 128 + rng.randint(-amount, amount)
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    out = img.convert("RGBA")
    out.alpha_composite(Image.merge("RGBA", (noise, noise, noise, Image.new("L",(w,h),18))))
    return out.convert("RGB")

def _orbit_dots_layer(size: Tuple[int,int], accent: Tuple[int,int,int]) -> Image.Image:
    # Minimal "work engine/orbit" motif: faint arcs + dots
    w, h = size
    layer = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    cx, cy = int(w*0.72), int(h*0.20)
    for r in (160, 240, 330):
        bbox = (cx-r, cy-r, cx+r, cy+r)
        d.arc(bbox, start=210, end=340, fill=(*accent, 60), width=3)
    rng = random.Random(21)
    for _ in range(24):
        r = rng.choice([160, 240, 330])
        ang = rng.uniform(210, 340) * math.pi / 180
        x = int(cx + math.cos(ang)*r)
        y = int(cy + math.sin(ang)*r)
        d.ellipse((x-6, y-6, x+6, y+6), fill=(*accent, 85))
    return layer

def _shadowed_card(base: Image.Image, rect, radius=34, shadow_alpha=70):
    w, h = base.size
    x0, y0, x1, y1 = rect
    shadow = Image.new("RGBA", (w, h), (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0+0, y0+10, x1+0, y1+10), radius=radius, fill=(0,0,0,shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    out = base.convert("RGBA")
    out.alpha_composite(shadow)
    return out.convert("RGB")

# ---------------------------------------------------------
# Receipt (clean, minimal)
# ---------------------------------------------------------
def render_receipt_png(receipt: Dict[str, Any], out_path: str):
    img = _linear_gradient((RECEIPT_W, RECEIPT_H), PAPER, PAPER_2)
    img = _add_soft_noise(img, amount=8)
    d = ImageDraw.Draw(img)

    mx, my = 60, 56
    card = (mx, my, RECEIPT_W - mx, RECEIPT_H - my)
    img = _shadowed_card(img, card, radius=34, shadow_alpha=60)
    d = ImageDraw.Draw(img)
    _rounded_rect(d, card, r=34, fill=(255,255,255), outline=HAIRLINE, width=3)

    x0, y0, x1, y1 = card
    pad = 46
    lx, rx = x0 + pad, x1 - pad
    y = y0 + pad

    title = _font(30, bold=True)
    sub = _font(18, bold=False)
    h2 = _font(22, bold=True)
    body = _font(18, bold=False)
    small = _font(16, bold=False)
    small_b = _font(16, bold=True)

    d.text((lx, y), "MARIA’S WORK MODE RECEIPT", font=title, fill=INK)
    y += 44
    d.text((lx, y), "Diagnosis • cost • reclaim plan", font=sub, fill=MUTED)
    y += 30
    d.line((lx, y, rx, y), fill=HAIRLINE, width=2)
    y += 26

    # Quick stats
    def stat(label, value):
        nonlocal y
        d.text((lx, y), label, font=small_b, fill=MUTED)
        d.text((lx + 430, y - 2), value, font=h2, fill=INK)
        y += 42

    stat("YOUR COORDINATION TAX", receipt.get("coordination_tax", ""))
    stat("DEEP WORK DISPLACED", receipt.get("focus_lost", ""))
    stat("RISK NEXT WEEK", receipt.get("risk", ""))

    y += 6
    d.line((lx, y, rx, y), fill=HAIRLINE, width=2)
    y += 22

    # House / Variant block
    house_key = receipt.get("house_key", "CURRENT")
    accent = HOUSE_STYLE.get(house_key, HOUSE_STYLE["CURRENT"])["accent"]

    # Accent rule
    d.rounded_rectangle((lx, y, rx, y+6), radius=3, fill=(*accent,))
    y += 22

    d.text((lx, y), "WORK MODE", font=small_b, fill=MUTED)
    d.text((lx + 90, y - 2), receipt.get("house_name", ""), font=h2, fill=INK)
    y += 34

    motto = receipt.get("house_motto", "")
    if motto:
        d.text((lx, y), motto, font=small, fill=MUTED)
        y += 30

    d.text((lx, y), "YOU ARE", font=small_b, fill=MUTED)
    d.text((lx + 140, y - 2), receipt.get("variant_name", ""), font=h2, fill=INK)
    y += 38

    d.text((lx, y), "WHAT IT MEANS", font=small_b, fill=MUTED)
    y += 26
    for ln in _wrap(d, receipt.get("variant_means", ""), body, rx - lx)[:3]:
        d.text((lx, y), ln, font=body, fill=INK)
        y += 28
    y += 8

    d.text((lx, y), "FASTEST WIN", font=small_b, fill=MUTED)
    y += 26
    for ln in _wrap(d, receipt.get("fastest_win", ""), body, rx - lx)[:3]:
        d.text((lx, y), ln, font=body, fill=INK)
        y += 28

    y += 12
    d.line((lx, y, rx, y), fill=HAIRLINE, width=2)
    y += 26

    d.text((lx, y), "MARIA WILL DO THIS FOR YOU (AT LAUNCH)", font=h2, fill=INK)
    y += 40
    for i, act in enumerate(receipt.get("maria_actions", [])[:3], start=1):
        if not _ensure_room(72):
            break
        d.text((lx, y), f"{i}.", font=small_b, fill=INK)
        lines = _wrap(d, act, body, rx - (lx + 30))
        yy = y
        for ln in lines[:2]:
            d.text((lx + 30, yy), ln, font=body, fill=INK)
            yy += 28
        y = yy + 10

    d.line((lx, y, rx, y), fill=HAIRLINE, width=2)
    y += 26

    d.text((lx, y), "YOUR 3-STEP RECLAIM PLAN", font=h2, fill=INK)
    y += 40
    for i, step in enumerate(receipt.get("reclaim_plan", [])[:3], start=1):
        if not _ensure_room(132):
            break
        d.text((lx, y), f"Step {i}", font=small_b, fill=MUTED)
        y += 24
        for ln in _wrap(d, step.get("action", ""), body, rx - lx)[:2]:
            d.text((lx, y), ln, font=body, fill=INK)
            y += 28
        d.text((lx, y), f"Impact: {step.get('impact', '')}", font=small, fill=MUTED)
        y += 34

    footer_y = y1 - pad - 54
    def _ensure_room(needed: int) -> bool:
        # Return True if there is room for 'needed' vertical pixels before footer.
        return (y + needed) <= (footer_y - 22)
    d.line((lx, footer_y - 18, rx, footer_y - 18), fill=HAIRLINE, width=2)
    for ln in _wrap(d, "Privacy: no titles/subjects/names. Ranges + normalized labels only.", small, rx - lx)[:2]:
        d.text((lx, footer_y), ln, font=small, fill=MUTED)
        footer_y += 20
    d.text((lx, footer_y + 24), "Chambiar • Get notified at launch", font=small, fill=MUTED)

    img.save(out_path, format="PNG")

# ---------------------------------------------------------
# Badge (aesthetic, "Chambiar.ai"-style)
# ---------------------------------------------------------
def render_badge_png(receipt: Dict[str, Any], out_path: str):
    house_key = receipt.get("house_key", "CURRENT")
    style = HOUSE_STYLE.get(house_key, HOUSE_STYLE["CURRENT"])
    accent = style["accent"]
    emoji = style["emoji"]

    # Background: warm-white → cool-white gradient + tiny texture + orbit motif
    bg = _linear_gradient((BADGE_W, BADGE_H), PAPER, PAPER_2)
    bg = _add_soft_noise(bg, amount=7)

    motif = _orbit_dots_layer((BADGE_W, BADGE_H), accent)
    bg_rgba = bg.convert("RGBA")
    bg_rgba.alpha_composite(motif)
    img = bg_rgba.convert("RGB")

    # Card: "invisible" glass — white with thin border + soft shadow
    mx, my = 68, 84
    card = (mx, my, BADGE_W - mx, BADGE_H - my)
    img = _shadowed_card(img, card, radius=36, shadow_alpha=55)
    d = ImageDraw.Draw(img)
    _rounded_rect(d, card, r=36, fill=(255, 255, 255), outline=HAIRLINE, width=3)

    x0, y0, x1, y1 = card
    pad = 52
    lx, rx = x0 + pad, x1 - pad
    y = y0 + pad

    # Subtle accent corner glow
    glow = Image.new("RGBA", img.size, (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((rx-420, y0-60, rx+220, y0+580), fill=(*accent, 55))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(glow)
    img = img_rgba.convert("RGB")
    d = ImageDraw.Draw(img)

    # Top line: "Work Week House" + thin accent rule
    label_f = _font(18, bold=True)
    d.text((lx, y), "WORK WEEK HOUSE", font=label_f, fill=MUTED)
    # Accent pill (tiny)
    pill = (lx + 208, y + 5, lx + 208 + 16, y + 21)
    d.rounded_rectangle(pill, radius=8, fill=accent)
    y += 30
    d.line((lx, y, rx, y), fill=HAIRLINE, width=2)
    y += 28

    # House name
    house_f = _font(54, bold=True)
    house_name = receipt.get("house_name", "The Current")
    d.text((lx, y), house_name, font=house_f, fill=INK)
    y += 70

    # Motto
    motto = receipt.get("house_motto", "")
    if motto:
        motto_f = _font(22, bold=False)
        for ln in _wrap(d, motto, motto_f, rx - lx)[:2]:
            d.text((lx, y), ln, font=motto_f, fill=MUTED)
            y += 30
        y += 8

    # Crest: minimal ring + emoji (kept small)
    crest_r = 54
    cx, cy = rx - crest_r, y0 + pad + 46
    d.ellipse((cx-crest_r, cy-crest_r, cx+crest_r, cy+crest_r), outline=(*accent, 220), width=4)
    d.ellipse((cx-crest_r+10, cy-crest_r+10, cx+crest_r-10, cy+crest_r-10), outline=HAIRLINE, width=3)
    crest_font = _font(36, bold=True)
    tw = d.textlength(emoji, font=crest_font)
    d.text((cx - tw/2, cy - 24), emoji, font=crest_font, fill=INK)

    # House strength
    strength = receipt.get("house_strength", "")
    if strength:
        d.text((lx, y), "HOUSE STRENGTH", font=_font(16, bold=True), fill=MUTED)
        y += 24
        strength_f = _font(22, bold=False)
        for ln in _wrap(d, strength, strength_f, rx - lx)[:2]:
            d.text((lx, y), ln, font=strength_f, fill=INK)
            y += 30
        y += 10

    d.line((lx, y, rx, y), fill=HAIRLINE, width=2)
    y += 28

    # Variant title (hero)
    d.text((lx, y - 6), "YOU ARE", font=_font(16, bold=True), fill=MUTED)
    y += 18
    v_f = _font(62, bold=True)
    variant = receipt.get("variant_name", "The Notification Storm")
    lines = _wrap(d, variant, v_f, rx - lx)[:2]
    for ln in lines:
        d.text((lx, y), ln, font=v_f, fill=INK)
        y += 72
    y += 8

    # Meaning
    means = receipt.get("variant_means", "")
    means_f = _font(24, bold=False)
    for ln in _wrap(d, means, means_f, rx - lx)[:3]:
        d.text((lx, y), ln, font=means_f, fill=MUTED)
        y += 34
    y += 10

    # Fastest win as "feature card"
    d.text((lx, y), "FASTEST WIN", font=_font(16, bold=True), fill=MUTED)
    y += 24
    win = receipt.get("fastest_win", "")
    box = (lx, y, rx, y + 132)
    _rounded_rect(d, box, r=24, fill=(*accent, 22), outline=(*accent, 120), width=2)

    win_f = _font(26, bold=True)
    yy = y + 16
    for ln in _wrap(d, win, win_f, (rx - lx) - 28)[:3]:
        d.text((lx + 14, yy), ln, font=win_f, fill=INK)
        yy += 34

    # Footer
    footer_y = y1 - pad - 52
    d.line((lx, footer_y - 18, rx, footer_y - 18), fill=HAIRLINE, width=2)
    small = _font(16, bold=False)
    d.text((lx, footer_y), "Share-safe • no titles/subjects/names", font=small, fill=MUTED)
    d.text((lx, footer_y + 26), "Chambiar • Get notified at launch", font=small, fill=MUTED)

    img.save(out_path, format="PNG")