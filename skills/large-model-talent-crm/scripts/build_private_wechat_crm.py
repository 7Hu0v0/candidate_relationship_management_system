#!/usr/bin/env python3
"""Build a private, local-only CRM webpage from a macOS WeChat account folder.

The script is intentionally lightweight: it reads filenames and short text
snippets under ``msg/file/``, ``temp/drag/``, and ``temp/Ann/`` and produces:

  - ``candidates.json``: reviewable candidate records.
  - ``index.html``: a static page for local browsing.

It does NOT decrypt SQLite databases, does NOT extract full PDF text, and does
NOT copy raw chat transcripts. Use ``--deep-pdf`` only for a small, deliberate
follow-up pass.

Typical usage:

    python3 scripts/build_private_wechat_crm.py \\
        --wechat-account ~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/<wxid_suffix> \\
        --output-dir private/wechat-crm \\
        --limit 200

The output directory should be git-ignored (see ``private/`` in ``.gitignore``).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import html
import json
import re
from pathlib import Path
from typing import Iterable

# Target company / lab keywords. Keep in sync with references/company_taxonomy.json.
COMPANY_PATTERNS: list[tuple[str, str]] = [
    ("OpenAI", r"openai|gpt-?4|chatgpt|codex|sora"),
    ("Anthropic", r"anthropic|claude"),
    ("Google DeepMind", r"deepmind|gemini|google\s+research|tpu|jax"),
    ("Meta AI", r"meta\s+ai|fair|\bllama\b|pytorch"),
    ("xAI", r"\bxai\b|grok"),
    ("Mistral AI", r"\bmistral\b"),
    ("Cohere", r"\bcohere\b|command\s+r"),
    ("DeepSeek", r"deepseek"),
    ("Moonshot AI", r"moonshot|kimi|月之暗面"),
    ("Zhipu AI", r"zhipu|智谱|\bglm\b"),
    ("MiniMax", r"minimax|海螺"),
    ("Baichuan", r"baichuan|百川"),
    ("StepFun", r"stepfun|阶跃"),
    ("01.AI", r"01\.ai|零一万物|\byi\s+model\b"),
    ("Alibaba Qwen", r"alibaba|aliyun|qwen|通义|modelscope"),
    ("Tencent Hunyuan", r"tencent|hunyuan|混元"),
    ("ByteDance Seed", r"bytedance|\bbyte\b|seed|doubao|豆包|字节"),
    ("Baidu ERNIE", r"baidu|ernie|文心|paddlepaddle"),
    ("Huawei Pangu", r"huawei|pangu|盘古|mindspore|ascend"),
    ("NVIDIA", r"nvidia|cuda|tensorrt|megatron"),
    ("AMD", r"\bamd\b|rocm"),
]

ROLE_PATTERNS: list[tuple[str, str]] = [
    ("pretraining", r"pretraining|预训练"),
    ("post_training", r"post[- ]?training|后训练|sft|rlhf|dpo|reward\s+model|alignment|对齐"),
    ("reasoning", r"reasoning|推理|reason"),
    ("multimodal", r"multimodal|多模态|vision|speech|video"),
    ("inference", r"inference|serving|quantization|kv\s*cache|推理|triton|vllm|tensorrt-?llm"),
    ("training_system", r"distributed\s+training|gpu|nccl|xla|megatron|deepspeed|训练系统|分布式"),
    ("data_eval", r"data\s+engine|synthetic\s+data|\beval|benchmark|annotation|safety|red\s*team|retrieval|\brag\b|评测|数据"),
    ("agent", r"\bagent\b|tool\s+use|browser|coding\s+assistant|copilot|workflow|ai\s+search|智能体|代码助手"),
]

RECOMMEND_HINTS = (
    "推荐",
    "内推",
    "候选人",
    "聊聊机会",
    "约一下",
    "简历",
    "candidate",
    "intro",
    "introduce",
    "referral",
)

TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".html", ".htm", ".json", ".csv"}
SCAN_FOLDERS = ("msg/file", "temp/drag", "temp/Ann")
MAX_TEXT_BYTES = 200_000  # do not read very large text-like files


def _now() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _stable_id(seed: str) -> str:
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:10]
    return f"local_{digest}"


def _safe_read_text(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return ""
        with path.open("rb") as f:
            data = f.read()
        # Reject obvious binary content.
        if b"\x00" in data:
            return ""
        return data.decode("utf-8", errors="ignore")
    except OSError:
        return ""


def _name_from_filename(name: str) -> str:
    base = re.sub(r"\.[A-Za-z0-9]+$", "", name)
    # Strip common noise like dates, wxid, "简历".
    base = re.sub(r"[\[(【]?\s*20\d{2}[-./]\d{1,2}([-./]\d{1,2})?\s*[\]】)】]?", " ", base)
    base = re.sub(r"wxid[_\-][A-Za-z0-9]+", " ", base, flags=re.IGNORECASE)
    base = re.sub(r"[\[(【]\s*resume|简历|候选人|cv\s*[\]】)】]", " ", base, flags=re.IGNORECASE)
    base = re.sub(r"[_\-.]+", " ", base)
    return base.strip() or name


def _match_companies(blob: str) -> list[str]:
    hits: list[str] = []
    lowered = blob.lower()
    for name, pattern in COMPANY_PATTERNS:
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            hits.append(name)
    return hits


def _match_roles(blob: str) -> list[str]:
    hits: list[str] = []
    lowered = blob.lower()
    for name, pattern in ROLE_PATTERNS:
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            hits.append(name)
    return hits


def _has_recommend_hint(blob: str) -> bool:
    lowered = blob.lower()
    return any(hint.lower() in lowered for hint in RECOMMEND_HINTS)


def _score_record(companies: list[str], roles: list[str], recommend: bool) -> int:
    score = 0
    if companies:
        score += 30
    score += min(len(roles) * 10, 30)
    if recommend:
        score += 20
    return min(score, 100)


def _iter_candidate_files(account: Path, deep_pdf: bool) -> Iterable[Path]:
    for relative in SCAN_FOLDERS:
        root = account / relative
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            if suffix in TEXT_EXTENSIONS:
                yield path
            elif deep_pdf and suffix == ".pdf":
                yield path
            elif deep_pdf and suffix in {".doc", ".docx"}:
                yield path


def _build_evidence(path: Path, snippet: str) -> dict[str, str]:
    parent = path.parent.name
    return {
        "source": "file" if parent != "Ann" else "ann",
        "path": str(path),
        "text": snippet[:240],
        "time": "unknown",
    }


def scan_account(account: Path, deep_pdf: bool, limit: int) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    seen_keys: set[str] = set()

    for path in sorted(_iter_candidate_files(account, deep_pdf)):
        if len(records) >= limit:
            break

        filename = path.name
        text = _safe_read_text(path) if path.suffix.lower() in TEXT_EXTENSIONS else ""
        blob = "\n".join([filename, text])
        companies = _match_companies(blob)
        roles = _match_roles(blob)
        recommend = _has_recommend_hint(blob)

        # Skip files with no signal at all to keep output reviewable.
        if not companies and not roles and not recommend:
            continue

        name = _name_from_filename(filename)
        dedupe_key = f"{name.lower()}|{','.join(sorted(companies))}"
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)

        snippet = text.strip().splitlines()[0] if text.strip() else filename
        record = {
            "id": _stable_id(dedupe_key),
            "name": name,
            "source_path": str(path),
            "companies": companies,
            "primary_company": companies[0] if companies else "unknown",
            "role_signals": roles,
            "has_recommend_hint": recommend,
            "score": _score_record(companies, roles, recommend),
            "evidence": [_build_evidence(path, snippet)],
            "scanned_at": _now(),
        }
        records.append(record)

    records.sort(key=lambda r: (-int(r["score"]), r["primary_company"], r["name"]))
    return records


def render_index(records: list[dict[str, object]], output: Path) -> None:
    rows = []
    for record in records:
        companies = ", ".join(record["companies"]) or "unknown"
        roles = ", ".join(record["role_signals"]) or "-"
        recommend_badge = "推荐" if record["has_recommend_hint"] else ""
        path = html.escape(str(record["source_path"]))
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(str(record['id']))}</code></td>"
            f"<td>{html.escape(str(record['name']))}</td>"
            f"<td>{html.escape(companies)}</td>"
            f"<td>{html.escape(roles)}</td>"
            f"<td>{record['score']}</td>"
            f"<td>{recommend_badge}</td>"
            f"<td class='path'>{path}</td>"
            "</tr>"
        )

    table_html = "\n".join(rows) or "<tr><td colspan='7'>无匹配结果</td></tr>"
    counts = {
        "total": len(records),
        "with_company": sum(1 for r in records if r["companies"]),
        "with_recommend": sum(1 for r in records if r["has_recommend_hint"]),
    }

    template = f"""<!doctype html>
<html lang=\"zh-CN\">
  <head>
    <meta charset=\"utf-8\">
    <title>Private WeChat CRM</title>
    <style>
      :root {{ color-scheme: light; font-family: Inter, -apple-system, system-ui, sans-serif; }}
      body {{ margin: 0; padding: 24px; background: #f6f7f9; color: #17202a; }}
      h1 {{ margin: 0 0 8px; font-size: 22px; }}
      p.muted {{ color: #697386; }}
      .summary {{ display: flex; gap: 16px; margin: 16px 0; }}
      .summary div {{ background: #fff; border: 1px solid #d9dee7; border-radius: 8px; padding: 12px 16px; min-width: 120px; }}
      table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #d9dee7; border-radius: 8px; overflow: hidden; }}
      th, td {{ padding: 10px 12px; border-bottom: 1px solid #d9dee7; text-align: left; vertical-align: top; font-size: 13px; }}
      th {{ background: #f1f5f9; color: #475569; }}
      td.path {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; color: #475569; word-break: break-all; }}
      code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }}
    </style>
  </head>
  <body>
    <h1>Private WeChat CRM (Local Only)</h1>
    <p class=\"muted\">本页面仅在本地生成，输出目录应加入 .gitignore。请人工复核后再用于外联。</p>
    <div class=\"summary\">
      <div><strong>{counts['total']}</strong><br>候选总数</div>
      <div><strong>{counts['with_company']}</strong><br>命中对标公司</div>
      <div><strong>{counts['with_recommend']}</strong><br>含推荐/内推字样</div>
    </div>
    <table>
      <thead>
        <tr><th>ID</th><th>姓名（来自文件名）</th><th>命中公司</th><th>角色信号</th><th>得分</th><th>提示</th><th>源路径</th></tr>
      </thead>
      <tbody>
        {table_html}
      </tbody>
    </table>
  </body>
</html>
"""
    output.write_text(template, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wechat-account", required=True, type=Path,
                        help="macOS WeChat account folder under xwechat_files/")
    parser.add_argument("--output-dir", required=True, type=Path,
                        help="Output directory for the private CRM (e.g. private/wechat-crm)")
    parser.add_argument("--limit", type=int, default=200,
                        help="Maximum number of candidate records to write")
    parser.add_argument("--deep-pdf", action="store_true",
                        help="Also scan .pdf and .docx files (slower; off by default)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    account = args.wechat_account.expanduser()
    output_dir = args.output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not account.exists():
        raise SystemExit(f"WeChat account folder not found: {account}")

    records = scan_account(account, deep_pdf=args.deep_pdf, limit=args.limit)
    payload = {
        "generated_at": _now(),
        "source_account": str(account),
        "summary": {
            "total": len(records),
            "with_company": sum(1 for r in records if r["companies"]),
            "with_recommend": sum(1 for r in records if r["has_recommend_hint"]),
        },
        "candidates": records,
    }

    json_path = output_dir / "candidates.json"
    html_path = output_dir / "index.html"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    render_index(records, html_path)

    print(f"Scanned {account}")
    print(f"Wrote {len(records)} candidates to {json_path}")
    print(f"Wrote local page to {html_path}")


if __name__ == "__main__":
    main()
