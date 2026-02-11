from __future__ import annotations
from typing import Dict, List, Tuple, Any
import datetime as dt

HOUSES: Dict[str, Dict[str, str]] = {
    "CALENDAR": {
        "name": "The Calendar",
        "motto": "Protect time. Create room to think.",
        "strength": "You show up, you align people, you keep things moving.",
        "shadow": "The week gets eaten by meetings and fragmentation."
    },
    "CURRENT": {
        "name": "The Current",
        "motto": "Calm the stream. Finish what matters.",
        "strength": "You’re responsive, plugged in, and available.",
        "shadow": "The inflow (messages/notifications) runs your day."
    },
    "COUNCIL": {
        "name": "The Council",
        "motto": "Decide faster. Clarify who owns the call.",
        "strength": "You’re thoughtful, inclusive, and risk-aware.",
        "shadow": "Decisions bottleneck; work stalls waiting for approval/alignment."
    },
    "GLUE": {
        "name": "The Glue",
        "motto": "Make ownership visible. Close loops.",
        "strength": "You connect dots, prevent chaos, and keep teams functioning.",
        "shadow": "You carry invisible coordination load without clear authority or recognition."
    }
}

VARIANTS: Dict[str, Dict[str, str]] = {
    "MEETING_PINBALL": {
        "house": "CALENDAR",
        "name": "The Meeting Pinball",
        "means": "Back-to-back meetings fragment focus and turn work into follow-ups.",
        "win": "Protect 2×90-minute focus blocks (3 days/week) + convert 1–2 recurring syncs to async."
    },
    "ASYNC_NEVER_HAPPENED": {
        "house": "CALENDAR",
        "name": "The Async-That-Never-Happened",
        "means": "You intend to work async, but updates aren’t structured—so meetings stay mandatory.",
        "win": "Require an async update template (status / blockers / decision needed) before scheduling meetings."
    },
    "INBOX_TRIAGE_NURSE": {
        "house": "CURRENT",
        "name": "The Inbox Triage Nurse",
        "means": "Everything feels urgent; threads get touched but not closed.",
        "win": "Two response windows/day + “owner + next step” rule on any thread you reply to."
    },
    "NOTIFICATION_STORM": {
        "house": "CURRENT",
        "name": "The Notification Storm",
        "means": "High message volume fractures attention and creates permanent behindness.",
        "win": "Set triage rules (urgent vs not) + move non-urgent into one daily digest channel."
    },
    "BOTTLENECK_MAGNET": {
        "house": "COUNCIL",
        "name": "The Bottleneck Magnet",
        "means": "Too many stakeholders or unclear decision owner stalls work.",
        "win": "One decision owner per workstream + a default decision window (e.g., 48 hours)."
    },
    "AFTER_HOURS_CREEP": {
        "house": "COUNCIL",
        "name": "The After-Hours Creep",
        "means": "Work spills into nights/weekends because boundaries and expectations are porous.",
        "win": "Set a boundary window (no meetings/no responses) + move recurring after-hours meetings by default."
    },
    "INVISIBLE_PM": {
        "house": "GLUE",
        "name": "The Invisible PM",
        "means": "You do hidden coordination (status chasing, clarifying ownership) that isn’t recognized.",
        "win": "Make ownership explicit: name an owner + next step for each commitment in one visible place."
    },
    "CONTEXT_SWITCH_TAXPAYER": {
        "house": "GLUE",
        "name": "The Context Switch Taxpayer",
        "means": "Interruptions and task switching inflate time-to-finish and mental load.",
        "win": "Batch comms + schedule focus mode blocks + standardize where “quick questions” go."
    },
}

ACTIONS_BY_AREA: Dict[str, List[str]] = {
    "MEETINGS": [
        "Draft agendas and capture decisions + owners (with your approval).",
        "Convert recurring syncs into async updates and route them to the right people.",
        "Track commitments from meetings and surface follow-ups before they slip."
    ],
    "FRAGMENTATION": [
        "Propose calendar protections for focus blocks and suggest meeting re-stacking.",
        "Bundle updates into async check-ins to reduce context switching.",
        "Summarize meeting-heavy days into a single action plan you can edit."
    ],
    "AFTER_HOURS": [
        "Flag after-hours patterns and suggest boundary rules you control.",
        "Propose rescheduling recurring meetings out of boundary windows.",
        "Create a lightweight ‘what’s truly urgent’ routing rule for late pings."
    ],
    "MESSAGE_PRESSURE": [
        "Summarize long threads into decisions/next steps without exposing content on the receipt.",
        "Draft replies and route threads to the right owner (with approval).",
        "Build a priority queue so the highest-impact items close first."
    ],
    "RESPONSE_LAG": [
        "Propose response windows and auto-drafts for common replies.",
        "Surface threads that need an owner, not just a response.",
        "Turn ‘waiting on’ items into a tracked follow-up list."
    ],
    "BOTTLENECKS": [
        "Detect stalled approvals and suggest the right nudge or escalation path.",
        "Clarify decision ownership and record decisions + rationale in one place.",
        "Generate a decision-ready brief from scattered updates (with approval)."
    ],
}

CHEAT_SHEET: List[Dict[str, str]] = [
    {"title":"Meetings / Fragmentation","signal":"High meeting load + split focus blocks","maria":"Convert repeats to async + capture decisions/owners","outcome":"More deep work, fewer circular meetings"},
    {"title":"After-hours creep","signal":"Work spilling past normal hours","maria":"Suggest boundary rules + flag chronic patterns","outcome":"Healthier schedules, less burnout risk"},
    {"title":"Email / message debt","signal":"Backlog + reply pressure rising","maria":"Draft replies, route threads, summarize chains","outcome":"Fewer dropped balls, faster closure"},
    {"title":"Notification overload","signal":"Interruptions breaking focus","maria":"Batching plan + digests; quiet hours controls","outcome":"Less context switching"},
    {"title":"Collaboration bottlenecks","signal":"Too many stakeholders / unclear owner","maria":"Clarify owner + decision path; record rationale","outcome":"Faster decisions, less rework"},
    {"title":"Onboarding / knowledge loss","signal":"Same questions repeating","maria":"Build living SOPs + searchable decision history","outcome":"Faster ramp, retained institutional memory"},
]

def _range_to_mid(r: str) -> float:
    r = (r or "").strip()
    if not r:
        return 0.0
    if r.endswith("+"):
        try:
            return float(r[:-1]) + 2.5
        except:
            return 0.0
    if "-" in r:
        a, b = r.split("-", 1)
        try:
            return (float(a) + float(b)) / 2.0
        except:
            return 0.0
    try:
        return float(r)
    except:
        return 0.0

def _scale(val: float, cuts: Tuple[float, float, float]) -> int:
    c1, c2, c3 = cuts
    if val <= c1:
        return 0
    if val <= c2:
        return 1
    if val <= c3:
        return 2
    return 3

FREQ_MAP = {
    "a few times": 1,
    "most days": 2,
    "every day": 3,
    "sometimes": 1,
    "constantly": 3,
    "a few times a day": 1,
    "every hour": 2,
    "multiple times an hour": 3,
    "yes": 2,
    "no": 0,
}

def normalize_survey(s: Dict[str, Any]) -> Dict[str, Any]:
    meeting_hours_mid = _range_to_mid(s.get("meeting_hours_range", ""))
    after_hours_mid = _range_to_mid(s.get("after_hours_hours_range", ""))
    email_backlog_mid = _range_to_mid(s.get("email_backlog_range", ""))

    fragmentation = FREQ_MAP.get(str(s.get("meet_interrupts", "")).lower(), 0)
    notif_press = FREQ_MAP.get(str(s.get("notif_interrupt_freq", "")).lower(), 0)
    email_behind = FREQ_MAP.get(str(s.get("email_behind_freq", "")).lower(), 0)
    response_press = 2 if str(s.get("response_pressure", "")).lower() == "yes" else 0

    collab_people = str(s.get("collab_people", "")).strip()
    bottlenecks = 0
    if collab_people in ("3-5", "3–5"):
        bottlenecks = 1
    elif collab_people in ("6-10", "6–10"):
        bottlenecks = 2
    elif collab_people in ("10+", "10＋"):
        bottlenecks = 3

    meetings = _scale(meeting_hours_mid, (5, 10, 15))
    after_hours = _scale(after_hours_mid, (0.5, 2, 4))
    message_press = max(_scale(email_backlog_mid, (10, 30, 60)), notif_press)
    response_lag = max(response_press, email_behind)

    def label4(score: int) -> str:
        return ["low", "moderate", "high", "severe"][max(0, min(3, score))]

    return {
        "ranges": {
            "meeting_hours": s.get("meeting_hours_range", ""),
            "after_hours_meeting_hours": s.get("after_hours_hours_range", ""),
            "email_backlog": s.get("email_backlog_range", ""),
        },
        "scores": {
            "MEETINGS": meetings,
            "FRAGMENTATION": fragmentation,
            "AFTER_HOURS": after_hours,
            "MESSAGE_PRESSURE": message_press,
            "RESPONSE_LAG": response_lag,
            "BOTTLENECKS": bottlenecks,
        },
        "areas": {
            "MEETINGS": label4(meetings),
            "FRAGMENTATION": label4(fragmentation),
            "AFTER_HOURS": label4(after_hours),
            "MESSAGE_PRESSURE": label4(message_press),
            "RESPONSE_LAG": label4(response_lag),
            "BOTTLENECKS": label4(bottlenecks),
        },
    }

def coordination_tax(signals: Dict[str, Any]) -> Tuple[str, str]:
    sc = signals["scores"]
    w = (
        sc["MEETINGS"] * 2
        + sc["FRAGMENTATION"] * 2
        + sc["MESSAGE_PRESSURE"] * 2
        + sc["RESPONSE_LAG"]
        + sc["AFTER_HOURS"]
        + sc["BOTTLENECKS"]
    )
    if w <= 3:
        return "5–8%", "1–3 hrs"
    if w <= 7:
        return "12–18%", "3–6 hrs"
    if w <= 12:
        return "18–26%", "6–9 hrs"
    return "26–35%", "9–12 hrs"

def risk_level(signals: Dict[str, Any]) -> str:
    r = max(
        signals["scores"]["AFTER_HOURS"],
        signals["scores"]["MESSAGE_PRESSURE"],
        signals["scores"]["BOTTLENECKS"],
    )
    return ["Low", "Moderate", "High", "High"][r]

def house_scores(signals: Dict[str, Any]) -> Dict[str, int]:
    sc = signals["scores"]
    return {
        "CALENDAR": 2 * sc["MEETINGS"] + 2 * sc["FRAGMENTATION"],
        "CURRENT": 2 * sc["MESSAGE_PRESSURE"] + sc["RESPONSE_LAG"] + sc["FRAGMENTATION"],
        "COUNCIL": 2 * sc["BOTTLENECKS"] + sc["MEETINGS"],
        "GLUE": 2 * sc["FRAGMENTATION"] + sc["BOTTLENECKS"] + sc["RESPONSE_LAG"],
    }

def pick_house(signals: Dict[str, Any]) -> str:
    hs = house_scores(signals)
    best = max(hs.values())
    tied = [k for k, v in hs.items() if v == best]
    if len(tied) == 1:
        return tied[0]
    sc = signals["scores"]
    if "CALENDAR" in tied and (sc["MEETINGS"] >= 2 and sc["FRAGMENTATION"] >= 2):
        return "CALENDAR"
    if "CURRENT" in tied and (sc["MESSAGE_PRESSURE"] >= 2):
        return "CURRENT"
    if "COUNCIL" in tied and (sc["BOTTLENECKS"] >= 2 or sc["AFTER_HOURS"] >= 2):
        return "COUNCIL"
    return tied[0]

def pick_variant(signals: Dict[str, Any], house: str) -> str:
    sc = signals["scores"]
    if house == "CALENDAR":
        return "MEETING_PINBALL" if (sc["MEETINGS"] >= 2 and sc["FRAGMENTATION"] >= 2) else "ASYNC_NEVER_HAPPENED"
    if house == "CURRENT":
        return "INBOX_TRIAGE_NURSE" if (sc["MESSAGE_PRESSURE"] >= 2 and sc["RESPONSE_LAG"] >= 2) else "NOTIFICATION_STORM"
    if house == "COUNCIL":
        if sc["AFTER_HOURS"] >= 2 and sc["BOTTLENECKS"] < 2:
            return "AFTER_HOURS_CREEP"
        if sc["BOTTLENECKS"] >= 2:
            return "BOTTLENECK_MAGNET"
        return "AFTER_HOURS_CREEP" if sc["AFTER_HOURS"] >= 1 else "BOTTLENECK_MAGNET"
    # GLUE
    return "CONTEXT_SWITCH_TAXPAYER" if sc["FRAGMENTATION"] >= 2 else "INVISIBLE_PM"

def top_areas(signals: Dict[str, Any], n: int = 2) -> List[str]:
    ranked = sorted(signals["scores"].items(), key=lambda kv: kv[1], reverse=True)
    return [k for k, _ in ranked[:n]]

def maria_actions_for(signals: Dict[str, Any], n: int = 3) -> List[str]:
    actions: List[str] = []
    for a in top_areas(signals, 2):
        actions.extend(ACTIONS_BY_AREA.get(a, []))
    out, seen = [], set()
    for x in actions:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out[:n]

def reclaim_plan(signals: Dict[str, Any]) -> List[Dict[str, str]]:
    plan: List[Dict[str, str]] = []
    for a in top_areas(signals, 3):
        if a == "MEETINGS":
            plan.append({"action": "Convert 1–2 recurring syncs to async updates", "impact": "~1–2 hrs/week"})
        elif a == "FRAGMENTATION":
            plan.append({"action": "Protect 2×90-minute focus blocks on 3 days", "impact": "~1–2 hrs/week"})
        elif a == "MESSAGE_PRESSURE":
            plan.append({"action": "Batch responses into 2 daily windows + triage rule", "impact": "~0.5–1.5 hrs/week"})
        elif a == "AFTER_HOURS":
            plan.append({"action": "Set a boundary window (no meetings / no-response)", "impact": "~0.5–1.5 hrs/week"})
        elif a == "BOTTLENECKS":
            plan.append({"action": "Assign a single decision owner + 48h decision window", "impact": "~0.5–2 hrs/week"})
        elif a == "RESPONSE_LAG":
            plan.append({"action": "Define response SLAs + owner routing for threads", "impact": "~0.5–1.5 hrs/week"})
    while len(plan) < 3:
        plan.append({"action": "Use one async update template (status/blockers/decision)", "impact": "~0.5–1.5 hrs/week"})
    return plan[:3]

def build_receipt(survey: Dict[str, Any]) -> Dict[str, Any]:
    signals = normalize_survey(survey)
    tax_pct, focus_lost = coordination_tax(signals)

    house_key = pick_house(signals)
    house = HOUSES[house_key]
    variant_key = pick_variant(signals, house_key)
    variant = VARIANTS[variant_key]

    return {
        "mode": "lite",
        "created_at": dt.datetime.utcnow().isoformat() + "Z",
        "week_of": survey.get("week_of", "Last week"),

        "coordination_tax": tax_pct,
        "focus_lost": focus_lost,
        "risk": risk_level(signals),

        "house_key": house_key,
        "house_name": house["name"],
        "house_motto": house["motto"],
        "house_strength": house["strength"],
        "house_shadow": house["shadow"],

        "variant_key": variant_key,
        "variant_name": variant["name"],
        "variant_means": variant["means"],
        "fastest_win": variant["win"],

        "maria_actions": maria_actions_for(signals),
        "reclaim_plan": reclaim_plan(signals),
        "cheat_sheet": CHEAT_SHEET,

        "signals": signals,
        "house_scores": house_scores(signals),
    }
