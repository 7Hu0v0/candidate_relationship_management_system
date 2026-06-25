# Large Model Talent CRM

一个面向大模型人才 sourcing 的轻量 CRM demo。

## Online Demo

[打开在线 Demo](https://7hu0v0.github.io/candidate_relationship_management_system/demo/)

## What It Shows

- 大模型人才 CRM 名单
- 搜索和优先级筛选
- 海外/国内公司分组
- 候选人详情和证据摘要
- 关系阶段、优先级、跟进状态、Owner 标记
- 简化管理员后台

管理员后台 demo 密码：

```text
jeffersonhu
```

## Data Notice

Demo 使用匿名样例数据，不包含真实姓名、手机号、邮箱或完整聊天记录。

## Project Structure

```text
index.html                            # Online demo entry (redirects to demo/)
demo/                                 # Static demo app
  index.html
  src/app.js
  src/styles.css
  data/crm_customers.json             # reviewable CRM records
  data/crm_customers.js               # offline fallback
  data/sample_contacts.json
  data/sample_chats.json
skills/large-model-talent-crm/
  SKILL.md                            # Codex/CodeBuddy skill entry
  agents/openai.yaml
  references/
    company-taxonomy.md
    company_taxonomy.json
    crm-schema.md
    demo-product-workflow.md
    sourcing-signal-channels.md
    wechat-local-scan.md
    local-private-web.md
  scripts/
    build_crm.py                      # contacts + chats -> crm_customers.json
    build_private_wechat_crm.py       # wechat folders -> private/wechat-crm/
private/                              # git-ignored, local-only CRM outputs
```

## Skill Scripts

Generate the demo JSON from sample contacts and chats:

```bash
python3 skills/large-model-talent-crm/scripts/build_crm.py \
  --contacts demo/data/sample_contacts.json \
  --chats demo/data/sample_chats.json \
  --taxonomy skills/large-model-talent-crm/references/company_taxonomy.json \
  --output demo/data/crm_customers.json
```

Generate a private local CRM webpage from a macOS WeChat account folder
(privacy-sensitive, output goes to `private/wechat-crm/` which is git-ignored):

```bash
python3 skills/large-model-talent-crm/scripts/build_private_wechat_crm.py \
  --wechat-account ~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/<wxid_suffix> \
  --output-dir private/wechat-crm \
  --limit 200
```

The script only reads filenames and short text-like snippets (`.txt`, `.md`,
`.html`, `.htm`, `.json`, `.csv`). It does NOT decrypt SQLite databases or copy
raw chat transcripts. Add `--deep-pdf` only for a deliberate follow-up pass.

## Privacy

- Treat WeCom/WeChat data as sensitive. The `private/` directory is git-ignored
  and is intended for local review only.
- Demo JSON ships with anonymized samples; do not commit real chat transcripts,
  phone numbers, or emails to the repository.
