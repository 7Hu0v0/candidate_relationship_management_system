#!/usr/bin/env python3
"""Build a reviewable large-model talent CRM JSON file from contacts and chats."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ACTIVE_WORDS = [
    "follow up", "intro", "interview", "offer", "hiring", "join", "candidate",
    "内推", "面试", "招聘", "候选人", "聊机会", "约", "推进", "简历",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def stable_id(userid: str, name: str) -> str:
    digest = hashlib.sha1((userid or name).encode("utf-8")).hexdigest()[:10]
    return f"talent_{digest}"


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def match_company(blob: str, taxonomy: dict[str, Any]) -> tuple[str, str, list[str]]:
    hits: list[str] = []
    for company in taxonomy.get("companies", []):
        name = company["name"]
        aliases = [name, *company.get("aliases", [])]
        if any(re.search(re.escape(alias.lower()), blob) for alias in aliases):
            hits.append(name)
    if not hits:
        return "unknown", "low", []
    tags = [f"company:{hits[0]}"] + [f"signal_company:{h}" for h in hits[1:]]
    return hits[0], "high" if len(hits) == 1 else "medium", tags


def match_roles(blob: str, taxonomy: dict[str, Any]) -> tuple[list[str], list[str]]:
    roles: list[str] = []
    for role, keywords in taxonomy.get("role_keywords", {}).items():
        if any(keyword.lower() in blob for keyword in keywords):
            roles.append(role)
    return roles, [f"role:{r}" for r in roles]


def chat_for_contact(contact: dict[str, Any], chats: list[dict[str, Any]]) -> dict[str, Any] | None:
    userid = str(contact.get("userid", ""))
    name = str(contact.get("name", ""))
    alias = str(contact.get("alias", ""))
    for chat in chats:
        if userid and userid == str(chat.get("chatid", "")):
            return chat
        if name and name == str(chat.get("chat_name", "")):
            return chat
        if alias and alias == str(chat.get("chat_name", "")):
            return chat
    return None


def summarize_evidence(contact: dict[str, Any], chat: dict[str, Any] | None) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    remark = contact.get("remark") or contact.get("alias") or ""
    if remark:
        evidence.append({"source": "remark", "text": str(remark)[:160], "time": "unknown"})
    if chat:
        for message in chat.get("messages", [])[:4]:
            text = str(message.get("text", "")).strip()
            if text:
                evidence.append({
                    "source": "chat",
                    "text": text[:180],
                    "time": str(message.get("time", "unknown")),
                })
    return evidence[:5]


def build_record(contact: dict[str, Any], chats: list[dict[str, Any]], taxonomy: dict[str, Any]) -> dict[str, Any]:
    chat = chat_for_contact(contact, chats)
    messages = chat.get("messages", []) if chat else []
    blob = "\n".join([
        str(contact.get("name", "")),
        str(contact.get("alias", "")),
        str(contact.get("remark", "")),
        "\n".join(str(m.get("text", "")) for m in messages),
    ]).lower()

    company, company_confidence, company_tags = match_company(blob, taxonomy)
    roles, role_tags = match_roles(blob, taxonomy)
    active = any(word in blob for word in ACTIVE_WORDS)
    warm = bool(messages)

    score = 0
    if company != "unknown":
        score += 30
    score += min(len(roles) * 10, 30)
    if active:
        score += 20
    if warm:
        score += 10
    score = min(score, 100)

    priority = "P0" if score >= 80 else "P1" if score >= 60 else "P2" if score >= 35 else "P3"
    if active:
        stage = "active"
        next_action = "Review recent context and schedule a focused follow-up."
    elif warm and score >= 35:
        stage = "warm"
        next_action = "Send a light-touch follow-up tied to the recent discussion."
    elif score >= 50:
        stage = "nurture"
        next_action = "Add to nurture list and look for a warm intro or new trigger."
    else:
        stage = "new"
        next_action = "Review manually before outreach."

    times = [parse_time(str(m.get("time", ""))) for m in messages]
    times = [t for t in times if t]
    last_contact_at = max(times).strftime("%Y-%m-%d %H:%M:%S") if times else "unknown"

    name = str(contact.get("name", "unknown"))
    userid = str(contact.get("userid", ""))
    tags = company_tags + role_tags
    if priority in ("P0", "P1"):
        tags.append("priority:high")

    return {
        "id": stable_id(userid, name),
        "name": name,
        "userid": userid,
        "alias": str(contact.get("alias", "")),
        "remark": str(contact.get("remark", "")),
        "company": company,
        "company_confidence": company_confidence,
        "role_signals": roles,
        "relationship_stage": stage,
        "priority": priority,
        "llm_relevance_score": score,
        "last_contact_at": last_contact_at,
        "next_action": next_action,
        "evidence": summarize_evidence(contact, chat),
        "tags": tags,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contacts", required=True, type=Path)
    parser.add_argument("--chats", required=True, type=Path)
    parser.add_argument("--taxonomy", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    contacts_data = load_json(args.contacts)
    chats_data = load_json(args.chats)
    taxonomy = load_json(args.taxonomy)
    contacts = contacts_data.get("userlist", contacts_data) if isinstance(contacts_data, dict) else contacts_data
    chats = chats_data.get("chats", chats_data) if isinstance(chats_data, dict) else chats_data

    records = [build_record(contact, chats, taxonomy) for contact in contacts]
    records.sort(key=lambda r: (r["priority"], -r["llm_relevance_score"], r["name"]))
    payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total": len(records),
            "priority_counts": {p: sum(1 for r in records if r["priority"] == p) for p in ["P0", "P1", "P2", "P3"]},
            "active_or_warm": sum(1 for r in records if r["relationship_stage"] in ["active", "warm"]),
        },
        "customers": records,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {len(records)} CRM records to {args.output}")


if __name__ == "__main__":
    main()
