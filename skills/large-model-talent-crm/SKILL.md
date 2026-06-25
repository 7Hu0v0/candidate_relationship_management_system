---
name: large-model-talent-crm
description: Build and update a CRM for large-model AI talent from visible WeCom/WeChat contacts, contact remarks or aliases, recent chat records, and target-company heuristics. Use when Codex needs to scan contacts, summarize recruiting or sourcing relationships, classify candidates by large-model company/lab signals, produce customer/candidate lists, or prepare a demo CRM dataset from chat-derived evidence.
---

# Large Model Talent CRM

## Purpose

Create a privacy-conscious CRM list for large-model talent sourcing. Combine visible contacts, contact remarks or aliases, recent chat evidence, and industry target-company definitions into structured records that can be reviewed before outreach.

## Data Sources

Prefer these sources in order:

1. Current visible WeCom contacts via `wecom-cli contact get_userlist '{}'`.
2. Recent chat list via `wecom-cli msg get_msg_chat_list '{"begin_time":"YYYY-MM-DD HH:mm:ss","end_time":"YYYY-MM-DD HH:mm:ss"}'`.
3. Recent messages per contact via `wecom-cli msg get_message '{"chat_type":1,"chatid":"USERID","begin_time":"YYYY-MM-DD HH:mm:ss","end_time":"YYYY-MM-DD HH:mm:ss"}'`.
4. Existing exported JSON files supplied by the user.

Follow the underlying WeCom skills' limits: message history is normally limited to the last 7 days, and contacts are only the current user's visible range. Do not send messages from this skill.

## Workflow

1. Read `references/company-taxonomy.md` when company matching or target-company scoring is needed.
2. Read `references/crm-schema.md` before creating or updating a CRM file.
3. Collect contacts and recent chats.
4. Normalize each person into the CRM schema:
   - `name`, `userid`, `alias`, `remark`
   - company/lab signals from remarks, aliases, and messages
   - large-model role signals
   - relationship stage and next action
   - evidence snippets with dates
5. Score each record conservatively. Prefer "unknown" over unsupported claims.
6. Run `scripts/build_crm.py` for deterministic JSON generation when source data is available as files.
7. Produce a reviewable list before any outreach. Keep private chat details summarized; avoid dumping raw chat logs unless the user explicitly asks.

## CLI Collection Pattern

Use a 7-day window unless the user gives a narrower valid range:

```bash
wecom-cli contact get_userlist '{}'
wecom-cli msg get_msg_chat_list '{"begin_time":"2026-06-18 00:00:00","end_time":"2026-06-25 23:59:59"}'
wecom-cli msg get_message '{"chat_type":1,"chatid":"USERID","begin_time":"2026-06-18 00:00:00","end_time":"2026-06-25 23:59:59"}'
```

For each chat, store only the minimum useful fields for CRM generation:

```json
{
  "chatid": "userid-or-chat-id",
  "chat_name": "Contact Name",
  "messages": [
    {"sender": "Contact Name", "time": "2026-06-24 14:20:00", "text": "short text"}
  ]
}
```

## CRM Heuristics

- Treat remarks and aliases as high-signal but not authoritative.
- Treat chat mentions as evidence, not facts, unless the person directly confirms them.
- Match company names, abbreviations, product names, and lab names against the taxonomy.
- Tag likely large-model areas such as pretraining, post-training, RLHF, inference, serving, data, eval, agents, multimodal, infra, GPU systems, search, and recommendation-to-LLM transfer.
- Assign relationship stages:
  - `new`: contact exists, no meaningful recruiting context.
  - `warm`: recent relevant conversation or clear mutual context.
  - `active`: explicit hiring, collaboration, intro, interview, or follow-up thread.
  - `nurture`: valuable long-term contact without immediate action.
- Use `confidence` values of `low`, `medium`, or `high`; never overstate private inferences.

## Script Usage

Generate demo or production-style JSON:

```bash
python3 skills/large-model-talent-crm/scripts/build_crm.py \
  --contacts demo/data/sample_contacts.json \
  --chats demo/data/sample_chats.json \
  --taxonomy skills/large-model-talent-crm/references/company_taxonomy.json \
  --output demo/data/crm_customers.json
```

The script expects JSON files and writes a CRM list plus summary metrics. It is safe for offline demo data and exported WeCom data shaped like the examples.

## Output Rules

- Default output is a table or JSON file with concise evidence.
- Do not include sensitive full chat transcripts in final CRM artifacts.
- Mark uncertain company, role, and intent fields as `unknown`.
- Include `next_action` only when supported by a remark or chat signal.
