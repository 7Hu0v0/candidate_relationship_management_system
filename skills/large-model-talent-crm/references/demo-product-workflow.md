# Demo Product Workflow

Use this reference when updating the static CRM demo under `demo/`.

## Product Shape

The demo should feel like a two-layer product:

- Front office workbench: talent CRM list, search, priority filtering, company folders, candidate detail, and local review/status edits.
- Admin backend: password gate, automation entry points, permission health, classification rules, and task logs.

Keep the first screen as the usable workbench, not a marketing page.

## Files

- `demo/index.html`: app shell, sidebar groups, workbench view, admin view.
- `demo/src/app.js`: state, filters, localStorage edits, admin unlock, simulated task log.
- `demo/src/styles.css`: responsive product UI.
- `demo/data/crm_customers.json`: display data.

## Front Office Requirements

The workbench should support:

- search over name, alias, remark, company, owner, follow-up status, tags, and role signals
- priority filter
- sidebar company filters:
  - 海外: OpenAI, Google, Anthropic, xAI, Meta
  - 国内: 字节, 阿里, 腾讯, 大模型六小龙
- candidate detail controls for:
  - relationship stage
  - priority
  - follow-up status
  - owner

Prototype edits should persist to `localStorage` and update the list immediately.

## Admin Requirements

Admin backend should be gated by a demo password. Current prototype password:

```text
jeffersonhu
```

This is a frontend-only demo gate, not production authentication.

Admin backend should include:

- automation command or entry point
- WeCom/WeChat permission health
- target-company classification rules
- task log
- a simulated run action that prepends a task log entry

If real WeCom/WeChat scans are blocked by permissions or encrypted databases, display `Blocked` or `Encrypted` honestly rather than hiding the issue.

## Implementation Notes

Use stable `data-view` and `data-company-filter` attributes for UI actions. Avoid server requirements; the demo should work as a static app, though `fetch()` requires serving from a local HTTP server for normal browser use.

Keep CRM evidence summarized and omit sensitive contact details from the visible page unless the user explicitly asks.

## Verification

Run:

```bash
node --check demo/src/app.js
python3 -m json.tool demo/data/crm_customers.json >/dev/null
python3 -m http.server 8001
```

Then verify:

- admin entry is visible from the sidebar
- wrong password is rejected
- `jeffersonhu` unlocks admin
- simulated run adds a log entry
- selecting a company folder filters the workbench
- changing follow-up status to `已约聊` updates the row
