# 微信公众号 → Notion（AIO 一体化页面版，UTC+8）

适配你的一体化页面：**Sources / Events / Rules（内联数据库）+ Daily Briefs（子页面）**。程序每天在 **UTC+8** 定时运行：
- 读取 **Sources**（只取 Enabled=✅ 的条目）
- 获取 RSS/页面，按 **Rules**（可在 Notion 内编辑）打分筛选
- 去重后写入 **Events**
- 在 **Daily Briefs** 下生成 `📅 YYYY-MM-DD 竞赛/活动简报`

> 你的一体化页面与字段已在 MCP 检查通过，可直接使用。

---

## 1) 必填环境变量（GitHub Secrets）
- `NOTION_TOKEN`：你的 Notion Internal Integration Token
- `NOTION_SOURCES_DB`：**Sources** 数据库 ID（比如 `07d6b2c9a6514d5ba492326672ae1ef1`）
- `NOTION_DB_ID`：**Events** 数据库 ID（比如 `976e5221486c4738952486a0f89f8db6`）
- `NOTION_RULES_DB`：**Rules** 数据库 ID（比如 `d97d3b23b83444a9b3c99cb678b2b926`）
- `NOTION_DAILY_PARENT`：**Daily Briefs** 父页面 ID（比如 `d6fe45e15afc46018e605d325c34d37e`）
- （可选 Variables）`TZ=Asia/Shanghai`

> 获取 ID：在 Notion 里点 **Open as full page**，复制 URL 中的 32 位 ID。确保这 4 个对象都 **Share 给该集成** 且权限 **Can edit**。

---

## 2) 本地运行（可选）
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export NOTION_TOKEN=secret_xxx
export NOTION_SOURCES_DB=07d6b2c9a6514d5ba492326672ae1ef1
export NOTION_DB_ID=976e5221486c4738952486a0f89f8db6
export NOTION_RULES_DB=d97d3b23b83444a9b3c99cb678b2b926
export NOTION_DAILY_PARENT=d6fe45e15afc46018e605d325c34d37e

python -m src.pipeline
```

---

## 3) GitHub Actions（推荐）
`.github/workflows/daily.yml` 默认 **每天 01:00 UTC（= 09:00 UTC+8）** 执行。若要改为 08:30 UTC+8，请把 cron 改为 `30 0 * * *`。

---

## 4) 规则与评分
- 规则动态读取自 **Rules** 库，字段：`Key / Pattern / Weight / HardBlock / Enabled`
- `MIN_SCORE` 的 `Weight` 作为最低阈值（为空则回退 3）
- 命中 `NEGATIVE` 且 `HardBlock=✅` 直接丢弃；否则按负分扣分
- `TRIGGERS_COMP`/`TRIGGERS_EVENT` 决定类型（若都命中，默认优先“竞赛”）；`PRIZE/ORG_AUTH/ONLINE/AUDIENCE` 叠加分
- 简单**截止时间提取**：匹配到 `YYYY-MM-DD / YYYY/MM/DD / 10月31日` 等样式 +2 分（可在代码里调）

---

## 5) 输出 & 去重
- **Events**：按 `Link` 去重（兜底 `Name+Source` 可自行加）
- **Daily Briefs**：列出当天命中的条目（标题/链接/类型/分数/来源）

---

## 6) 常见问题
- 运行后 Events 没有新增？检查：① Sources 是否勾选 Enabled；② Rules 的阈值是否过高；③ Feed 是否可达；④ 集成权限是否 **Can edit**。
- 想加“数学建模/互联网+/大创/ACM-ICPC”等关键词？直接在 **Rules** 库新增对应 `Key=TRIGGERS_COMP/AUDIENCE/PRIZE/ORG_AUTH` 的规则，或给我要一份 CSV。

