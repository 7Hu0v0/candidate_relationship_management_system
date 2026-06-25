# Private Local CRM Webpage

Use this reference when generating a local-only CRM page from the user's macOS WeChat artifacts, including received files, readable text/HTML notes, recommendation signals, and target-company keywords.

## Shape

- Skill entry: `skills/large-model-talent-crm/SKILL.md`
- Script: `skills/large-model-talent-crm/scripts/build_private_wechat_crm.py`
- Private output: `private/wechat-crm/index.html` and `private/wechat-crm/candidates.json`
- Git safety: `private/` must be ignored.

## Workflow

1. Confirm whether the user is asking for a private local page or the public open-source demo.
2. For private local pages, inspect WeChat account roots under:

```text
~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/
```

3. Prefer readable local signal folders:

```text
<account>/msg/file/
<account>/temp/drag/
<account>/temp/Ann/
```

4. Check message/contact/session databases only to determine readability. If `sqlite3` reports `file is not a database`, record them as encrypted or packaged and fall back to attachments.
5. Run `build_private_wechat_crm.py` with the account root and `private/wechat-crm` output. The script accepts both resume-style artifacts and readable `推荐 + 对标公司` keyword signals.
6. Serve the local page from `private/wechat-crm` with a localhost-only server when the user wants to browse it.

## Privacy Rules

- Do not publish private outputs.
- Do not copy raw chat transcripts into the public demo.
- Prefer filename and concise evidence summaries.
- Keep source file paths visible in the private page so the user can manually verify high-priority contacts.
- Add `private/` to `.gitignore` before the first run.
