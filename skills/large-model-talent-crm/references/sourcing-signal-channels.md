# WeChat Sourcing Signal Channels

Use this reference when the user asks to continue mining WeChat records for large-model talent leads beyond resume attachments.

## Target Keywords

Prioritize explicit recommendation and counterpart-company signals:

```text
推荐
字节 ByteDance Seed 豆包 TikTok 飞书
阿里 Alibaba 通义 Qwen 千问 蚂蚁 高德
Meta Llama FAIR PyTorch
xAI Grok
Google DeepMind Gemini
OpenAI Anthropic DeepSeek Kimi Moonshot 智谱 GLM MiniMax 阶跃 StepFun 百川 01.AI
大模型 后训练 Agent 智能体 推理 多模态 评测 数据 infra GPU
```

## Channel Inventory

Scan channels in this order.

1. **Visible WeCom contacts**: contact names, aliases, departments, and remarks from `wecom-cli contact get_userlist '{}'`. This is the cleanest path for "联系人备注有对标公司".
2. **WeCom recent chats**: `wecom-cli msg get_msg_chat_list` and `wecom-cli msg get_message` for the last 7 days. Look for `推荐 + company`, explicit introductions, and role/company mentions.
3. **macOS WeChat contact/session/message DBs**:
   - `db_storage/contact/contact.db`
   - `db_storage/contact/contact_fts.db`
   - `db_storage/session/session.db`
   - `db_storage/message/message_*.db`
   - `db_storage/message/message_fts.db`
   - `db_storage/favorite/favorite.db`
   Check with `sqlite3 "$DB" .tables`. If it says `file is not a database`, treat the channel as encrypted/packaged and record it as blocked.
4. **Readable received files**: `<account>/msg/file/**`. Scan filenames first, then selected PDF/text content only when needed.
5. **Temporary dropped/shared files**: `<account>/temp/drag/**`.
6. **Announcement/link HTML**: `<account>/temp/Ann/*.htm`. These can contain forwarded web pages, shared notes, recommendation text, or extracted link previews.
7. **Favorite/export artifacts**: `<account>/business/favorite/**` and `db_storage/favorite/*` when readable.
8. **Message caches**: `<account>/cache/*/Message/**` and `<account>/msg/attach/**`. Treat as low-confidence; many files are binary and cause false positive ASCII hits such as `xAI`.
9. **Backup packages**: `Backup/<wxid>/<backup-id>/files/1/**`. Usually packaged/encrypted. Use only for structure and size unless readable documents appear.

## Evidence Rules

- A strong lead has either a person identifier plus target company, or a direct recommendation phrase plus company/role context.
- A weak lead has only a company keyword in binary/cache data or in a generic industry report; do not turn this into a contact.
- For contact remarks, prefer exported/visible contact APIs. If local contact DB is encrypted, say `contact remarks blocked`.
- Do not copy full chat logs. Store concise evidence such as: `聊天/备注提到推荐字节 Seed agent 候选人，需复核联系人`.

## Triage Commands

Keyword scan readable text-like artifacts:

```bash
rg -a -i -n --max-filesize 5M '推荐|字节|ByteDance|阿里|Alibaba|通义|Qwen|Meta|xAI|Google|DeepMind|OpenAI|Anthropic|DeepSeek|Kimi|智谱|MiniMax|阶跃|大模型|后训练|Agent|智能体|推理|多模态' "$ACCOUNT/msg/file" "$ACCOUNT/temp/drag" "$ACCOUNT/temp/Ann"
```

Check database readability:

```bash
for db in contact/contact.db contact/contact_fts.db session/session.db message/message_fts.db favorite/favorite.db; do
  sqlite3 "$ACCOUNT/db_storage/$db" .tables
done
```

Run the private local CRM builder:

```bash
python3 skills/large-model-talent-crm/scripts/build_private_wechat_crm.py \
  --wechat-account "$ACCOUNT" \
  --output-dir private/wechat-crm \
  --limit 200
```
