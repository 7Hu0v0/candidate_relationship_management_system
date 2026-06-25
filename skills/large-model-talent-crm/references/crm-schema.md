# CRM Schema

Each CRM record should be reviewable and traceable.

```json
{
  "id": "stable-id",
  "name": "Person Name",
  "userid": "wecom-userid",
  "alias": "alias or empty",
  "remark": "contact remark if available",
  "company": "matched company or unknown",
  "company_confidence": "low|medium|high",
  "role_signals": ["infra", "post-training"],
  "relationship_stage": "new|warm|active|nurture",
  "priority": "P0|P1|P2|P3",
  "llm_relevance_score": 0,
  "last_contact_at": "YYYY-MM-DD HH:mm:ss or unknown",
  "next_action": "short action or review",
  "evidence": [
    {"source": "remark|chat", "text": "short non-sensitive summary", "time": "YYYY-MM-DD HH:mm:ss or unknown"}
  ],
  "tags": ["company:DeepSeek", "role:infra"]
}
```

## Scoring

- Start at 0.
- Add 30 for a matched target company.
- Add 10 per role category, up to 30.
- Add 20 for active relationship signals.
- Add 10 for warm recent conversation.
- Cap at 100.

Priority:

- `P0`: score >= 80
- `P1`: score 60-79
- `P2`: score 35-59
- `P3`: score < 35

## Evidence Rules

- Keep evidence short and paraphrased.
- Include raw wording only when it is brief and necessary.
- Use `unknown` rather than guessing.
