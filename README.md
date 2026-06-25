# Candidate Relationship Management System

一个面向“大模型人才”的轻量 CRM 原型：从可见通讯录、联系人备注、最近聊天摘要、本地微信可读文件和简历/纪要证据里，整理候选客户名单、优先级、关系阶段和下一步动作。

## What is included

- `skills/large-model-talent-crm/`: Codex skill，描述如何用 `wecom-cli`、本地微信文件、简历/纪要证据生成 CRM。
- `skills/large-model-talent-crm/scripts/build_crm.py`: 离线 JSON 生成脚本。
- `skills/large-model-talent-crm/references/wechat-local-scan.md`: macOS 微信数据定位、加密库判断和可读线索抽取流程。
- `skills/large-model-talent-crm/references/demo-product-workflow.md`: demo 前台工作台和管理员后台的产品化流程。
- `demo/`: 静态 CRM demo 页面，包含前台工作台和管理员后台。
- `demo/data/sample_contacts.json` 和 `demo/data/sample_chats.json`: 脱敏示例输入。
- `demo/data/crm_customers.json`: 由脚本生成的 demo 输出。

## Demo product shape

前台工作台：

- 展示大模型人才 CRM 名单
- 搜索、按优先级筛选
- 左侧公司文件夹筛选：海外 OpenAI / Google / Anthropic / xAI / Meta；国内字节 / 阿里 / 腾讯 / 大模型六小龙
- 候选人详情可标记关系阶段、优先级、跟进状态、Owner
- 标记状态保存在浏览器本地，并同步更新列表

管理员后台：

- 入口在左侧侧边栏
- demo 密码：`jeffersonhu`
- 展示自动化抓取入口、WeCom/微信权限健康度、分类规则和任务日志
- “模拟运行”会新增一条任务日志

注意：管理员密码是静态 demo 的前端保护，不是生产级鉴权。

## Generate the demo CRM data

```bash
python3 skills/large-model-talent-crm/scripts/build_crm.py \
  --contacts demo/data/sample_contacts.json \
  --chats demo/data/sample_chats.json \
  --taxonomy skills/large-model-talent-crm/references/company_taxonomy.json \
  --output demo/data/crm_customers.json
```

## View the demo

推荐从 repo 根目录启动本地服务：

```bash
python3 -m http.server 8001
```

Then open `http://localhost:8001/demo/`.

也可以直接打开：

```text
demo/index.html
```

页面会优先读取 `demo/data/crm_customers.json`，如果浏览器在 `file://` 下拦截 JSON 读取，会自动使用 `demo/data/crm_customers.js` 作为本地 fallback。

## Local WeChat sourcing

当用户提供 macOS 微信路径时，优先参考：

```text
skills/large-model-talent-crm/references/wechat-local-scan.md
```

流程要点：

- 先判断目录是 `Backup/.../files/1` 备份包，还是 `xwechat_files/<wxid>_<suffix>` 活跃账号目录。
- `Backup` 目录通常包含 `Index/`、`ChatPackage/`、`Media/`，可确认是聊天备份，但通常不是可直接读取的文本。
- `db_storage/message/*.db`、`contact/*.db` 可能是加密/封装数据库；如果 `sqlite3` 提示 `file is not a database`，标记为 `Encrypted` 或 `Blocked`。
- 优先从 `msg/file/`、`temp/drag/`、会议纪要、简历、HTML/Markdown 文档里抽取可确认候选线索。
- CRM 只保存证据摘要，不默认展示手机号、邮箱、完整私聊原文。

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
