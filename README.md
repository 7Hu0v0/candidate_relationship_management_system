# Candidate Relationship Management System

一个面向“大模型人才”的轻量 CRM 原型：从可见通讯录、联系人备注和最近聊天摘要里，整理候选客户名单、优先级、关系阶段和下一步动作。

## What is included

- `skills/large-model-talent-crm/`: Codex skill，描述如何用 `wecom-cli` 通讯录和消息接口生成 CRM。
- `skills/large-model-talent-crm/scripts/build_crm.py`: 离线 JSON 生成脚本。
- `demo/`: 静态 CRM demo 页面。
- `demo/data/sample_contacts.json` 和 `demo/data/sample_chats.json`: 脱敏示例输入。
- `demo/data/crm_customers.json`: 由脚本生成的 demo 输出。

## Generate the demo CRM data

```bash
python3 skills/large-model-talent-crm/scripts/build_crm.py \
  --contacts demo/data/sample_contacts.json \
  --chats demo/data/sample_chats.json \
  --taxonomy skills/large-model-talent-crm/references/company_taxonomy.json \
  --output demo/data/crm_customers.json
```

## View the demo

Because the demo uses `fetch`, serve it from the repo root:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/demo/`.

## Real data shape

The skill expects WeCom-style contacts:

```json
{
  "userlist": [
    {"userid": "zhangsan", "name": "张三", "alias": "Sam", "remark": "Qwen infra"}
  ]
}
```

And compact chat exports:

```json
{
  "chats": [
    {
      "chatid": "zhangsan",
      "chat_name": "张三",
      "messages": [
        {"sender": "张三", "time": "2026-06-24 12:00:00", "text": "最近在做 inference serving"}
      ]
    }
  ]
}
```

Raw chat logs should stay local and summarized. The CRM output keeps only short evidence snippets for review.
