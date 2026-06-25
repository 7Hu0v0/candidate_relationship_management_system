# macOS WeChat Local Scan

Use this reference when the user points at local WeChat data under:

```text
~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/
```

## Safety

- Treat WeChat data as sensitive. Inspect structure first, then extract only minimal CRM evidence.
- Do not delete, move, decrypt, or upload local WeChat files unless the user explicitly asks and the action is safe.
- Do not put phone numbers, emails, full chat transcripts, or raw private messages into demo CRM output by default.
- Prefer concise evidence summaries with a source filename and month.

## Useful Path Types

Backup packages often look like:

```text
xwechat_files/Backup/<wxid>/<backup-id>/files/1/
```

This structure usually contains:

- `pkg_info.dat`, `pkg.attr`, `backup_time.dat`, `detail.dat`, `tar_index.dat`
- per-conversation hash directories
- `Index/`, `ChatPackage/`, and sometimes `Media/`
- `Media/*.tar.enc` and media payloads that can dominate disk usage

This confirms a WeChat chat backup package, but it is not a normal text chat export.

Active local account data often looks like:

```text
xwechat_files/<wxid>_<suffix>/
  db_storage/contact/
  db_storage/message/
  db_storage/session/
  msg/file/
  temp/drag/
```

This is better for sourcing. Look for readable resumes, meeting notes, exported HTML, Markdown, TXT, DOCX, and PDFs under `msg/file/` and `temp/drag/`.

## Triage Commands

Measure size and shape:

```bash
du -sh "$PATH"
find "$PATH" -maxdepth 3 -type d -print
find "$PATH" -type f | wc -l
```

Identify backup internals:

```bash
find "$BACKUP/files/1" -mindepth 2 -maxdepth 2 -type d -print | sed 's#.*/##' | sort | uniq -c | sort -nr
find "$BACKUP/files/1" -type f -name '*.enc' -print | wc -l
find "$BACKUP/files/1" -type f -size +1M -print | head -n 30
```

Find local databases and readable files:

```bash
find "$XWECHAT" -type f \( -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' -o -name '*contact*' -o -name '*message*' \) -print
find "$ACCOUNT/msg/file" "$ACCOUNT/temp/drag" -type f -print
```

Search readable files for target-company and role signals:

```bash
rg -a -n --max-filesize 5M 'DeepSeek|Kimi|Moonshot|智谱|GLM|MiniMax|阶跃|Qwen|通义|阿里|混元|腾讯|Seed|豆包|字节|OpenAI|Anthropic|Claude|Meta|NVIDIA|CUDA|大模型|AI产品|Agent|RAG|推理|训练' "$ACCOUNT/msg/file" "$ACCOUNT/temp"
```

Avoid treating binary `ChatPackage` hits as facts. Short ASCII strings such as `GLM` can appear randomly in encrypted/binary data.

## Database Interpretation

Check whether a `.db` is real SQLite:

```bash
file "$DB"
xxd -l 128 "$DB"
sqlite3 "$DB" '.tables'
```

If `sqlite3` says `file is not a database`, or the header is not `SQLite format 3`, treat it as encrypted/packaged. Record that as `Blocked` or `Encrypted`. Do not claim the messages were scanned.

`all_users/login/<wxid>/key_info.db` may be normal SQLite, but that does not mean message databases are readable. If `sqlcipher` or a known safe decryptor is unavailable, fall back to readable files and explicit exported data.

## Candidate Extraction

For PDFs, use bundled Python with `pdfplumber` or `pypdf` to extract a few pages. For text/HTML/Markdown, use `sed` or `rg`. Extract:

- name
- current and prior companies
- large-model role signals
- relationship/evidence source
- source file and date if available

Examples of high-signal sources:

- resume file names under `temp/drag/` or `msg/file/`
- meeting notes such as `【强将交流】-<name>-元宝纪要.txt`
- HTML dashboards with candidate rows
- exported Markdown notes with owner or company context

## CRM Mapping

Map each confirmed person into `references/crm-schema.md`. Keep `evidence[].text` short and paraphrased:

```json
{
  "source": "cv",
  "text": "CV shows current Alibaba Qwen AI product work on multimodal QA agent strategy and evaluation.",
  "time": "2026-05"
}
```

If source confidence is partial, mark `company_confidence` as `medium` or `low`, and say "需二次确认" in `next_action`.
