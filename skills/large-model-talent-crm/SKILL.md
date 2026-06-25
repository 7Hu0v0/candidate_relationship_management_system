---
name: large-model-talent-crm
description: Build and update a CRM for large-model AI talent from visible WeCom/WeChat contacts, local WeChat files, contact remarks or aliases, recent chat records, resume/meeting-note evidence, and target-company heuristics. Use when Codex needs to scan WeCom or macOS WeChat data, diagnose encrypted local chat stores, extract candidate leads from readable chat-adjacent files, generate a private local CRM webpage from WeChat attachments, classify candidates by large-model company/lab signals, update the public demo CRM frontend/admin experience, or prepare a reviewable CRM dataset from chat-derived evidence.
---

# Large Model Talent CRM

## Purpose

Create a privacy-conscious CRM list for large-model talent sourcing. Combine visible contacts, contact remarks or aliases, recent chat evidence, and industry target-company definitions into structured records that can be reviewed before outreach.

## Data Sources

Prefer these sources in order:

1. Current visible WeCom contacts via `wecom-cli contact get_userlist '{}'`.
2. Recent chat list via `wecom-cli msg get_msg_chat_list '{"begin_time":"YYYY-MM-DD HH:mm:ss","end_time":"YYYY-MM-DD HH:mm:ss"}'`.
3. Recent messages per contact via `wecom-cli msg get_message '{"chat_type":1,"chatid":"USERID","begin_time":"YYYY-MM-DD HH:mm:ss","end_time":"YYYY-MM-DD HH:mm:ss"}'`.
4. Local macOS WeChat data under `~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/`.
5. Existing exported JSON, resumes, meeting notes, and local files supplied by the user.

Follow the underlying WeCom skills' limits: message history is normally limited to the last 7 days, and contacts are only the current user's visible range. Do not send messages from this skill.

## Workflow

1. Read `references/company-taxonomy.md` and `references/company_taxonomy.json` when company matching or target-company scoring is needed.
2. Read `references/crm-schema.md` before creating or updating a CRM file.
3. For macOS WeChat folders, read `references/wechat-local-scan.md` before scanning or interpreting local backup/database paths.
4. For broad WeChat sourcing beyond resumes, read `references/sourcing-signal-channels.md`.
5. For private local webpages generated from WeChat files, read `references/local-private-web.md`.
6. For public website/product updates, read `references/demo-product-workflow.md` before editing `demo/`.
7. Collect contacts, recent chats, local readable files, or exported artifacts.
8. Normalize each person into the CRM schema:
   - `name`, `userid`, `alias`, `remark`
   - company/lab signals from remarks, aliases, and messages
   - large-model role signals
   - relationship stage and next action
   - evidence snippets with dates
9. Score each record conservatively. Prefer "unknown" over unsupported claims.
10. Run `scripts/build_crm.py` for deterministic JSON generation when source data is available as files.
11. Run `scripts/build_private_wechat_crm.py` to scan a WeChat account folder and produce a private local CRM webpage under `private/wechat-crm/` (git-ignored).
12. Produce a reviewable list before any outreach. Keep private chat details summarized; avoid dumping raw chat logs unless the user explicitly asks.

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

Generate demo or production-style JSON from contacts + chats:

```bash
python3 skills/large-model-talent-crm/scripts/build_crm.py \
  --contacts demo/data/sample_contacts.json \
  --chats demo/data/sample_chats.json \
  --taxonomy skills/large-model-talent-crm/references/company_taxonomy.json \
  --output demo/data/crm_customers.json
```

The script expects JSON files and writes a CRM list plus summary metrics. It is safe for offline demo data and exported WeCom data shaped like the examples.

Generate a private local CRM webpage from a macOS WeChat account folder:

```bash
python3 skills/large-model-talent-crm/scripts/build_private_wechat_crm.py \
  --wechat-account ~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/<wxid_suffix> \
  --output-dir private/wechat-crm \
  --limit 200
```

The script reads filenames, recent text notes, and small Markdown/HTML/TXT snippets under `msg/file/`, `temp/drag/`, and `temp/Ann/`. It is deliberately lightweight: no PDF text extraction, no DB decryption. Use `--deep-pdf` only for a small, deliberate follow-up pass. The output goes to `private/wechat-crm/` and is intended for local review only — `private/` must be git-ignored.

## Demo Product Pattern

The demo is a static frontend under `demo/`:

- `demo/index.html`: shell, sidebar, workbench, and admin sections.
- `demo/src/app.js`: loading, filtering, local status edits, password-gated admin, and task logs.
- `demo/src/styles.css`: layout and interaction styling.
- `demo/data/crm_customers.json` plus the `crm_customers.js` fallback: reviewable CRM records displayed by the frontend.

Use browser-local storage for prototype-only state such as relationship stage, priority, follow-up status, owner, admin unlock, and simulated task logs. Treat frontend passwords as demo gates only; do not describe them as production authentication.

## Output Rules

- Default output is a table or JSON file with concise evidence.
- Do not include sensitive full chat transcripts in final CRM artifacts.
- Mark uncertain company, role, and intent fields as `unknown`.
- Include `next_action` only when supported by a remark or chat signal.
- Never commit `private/`. It is a personal working directory, not a public artifact.
