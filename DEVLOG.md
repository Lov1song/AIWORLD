# 异界编年史 · 开发日志

> 一款基于 AI 的单文件沉浸式文字 RPG

---

## v0.1 · 初始版本

**日期：** 2026-05-11

### 项目概述

单文件 HTML 游戏，无任何外部框架依赖。玩家自定义世界观与角色，由 AI 担任 GM 实时生成剧情，支持属性检定与骰子判定。

### 技术栈

- **前端**：纯 HTML / CSS / JavaScript
- **AI 模型**：阿里云 DashScope `qwen-plus`，SSE 流式输出
- **字体**：Cinzel（标题）、Noto Serif SC（正文），Google Fonts

### 已实现功能

**世界构建面板**
- 4 种内置世界模板：奇幻大陆、赛博废土、修仙界、末日荒原，支持自定义
- 自由填写世界背景与角色背景
- 角色命名

**属性系统**
- 4 项属性：力量、智慧、魅力、敏捷，基础值 5
- 初始 10 点自由分配，单项上限 15

**游戏面板**
- 侧边栏：HP 血条、属性数值、金币、回合数、骰子结果、事件日志
- 故事区：AI 流式打字输出（分块刷新）
- 选项区：AI 生成 2-3 个行动选项按钮
- 自由输入框：玩家可输入任意行动

**骰子判定**
- D20 + 属性修正值（每超过基准值 2 点 +1）
- 关键词自动匹配检定属性（攻击→力量、说服→魅力等）
- ≥15 大成功 / ≥6 部分成功 / <6 失败

**GM 指令系统**
- AI 回复末尾嵌入 `[[HP:±N]]` `[[GOLD:±N]]` `[[STR/INT/CHA/AGI:±N]]` 指令
- 前端解析后实时更新角色数据

**其他**
- 历史记录保留最近 14 条消息传入 AI
- 事件日志最多显示 20 条
- 移动端响应式布局

### 已知问题 / 待优化

- API Key 硬编码在前端，存在安全风险
- 打字效果为分块刷新，不够流畅
- 骰子无动画，数字直接跳出
- 无本地存档，刷新即丢失进度
- 选项无快捷键，全靠鼠标点击
- 无背包/道具系统
- 属性无成长机制

---

## v0.2 · 体验优化

**日期：** 2026-05-11

### 改动内容

**快捷键选项**
- 游戏面板中按 `1` / `2` / `3` 直接触发对应选项，焦点在输入框时不触发

**骰子滚动动画**
- 投掷时数字以 50ms 间隔快速随机跳动，持续约 650ms 后定格真实结果
- 定格时有弹性缩放动画（`diceSettle`），失败/成功颜色随结果变化

**逐字打字效果 + 点击跳过**
- 解耦流式接收与显示：SSE delta 推入字符缓冲队列，`setInterval` 以 20ms/字 逐字渲染
- 指令标记（`[[...]]`）和选项标签在缓冲阶段过滤，不会显示给玩家
- 点击故事区立即跳过动画，显示完整文本
- 打字期间故事区显示"点击跳过"提示和手型光标（`typing-active` class）
- 修复：跳过后流式数据仍推字符导致动画重启的问题（加 `skipped` 标志）

**背包系统**
- `gs.items[]` 存储道具列表
- AI 可通过 `[[ITEM:+道具名]]` / `[[ITEM:-道具名]]` 发放或移除道具
- 侧边栏新增"背包"栏，有道具时自动显示，为空时隐藏
- System prompt 补充背包状态与指令说明，AI 可感知当前持有物品

---

## v0.3 · 后端架构 + 接口开发

**日期：** 2026-05-11

### 架构转型

从单文件 HTML 转型为前后端分离 Web 应用：

```
ai-world-game/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── game.py
│   │   └── ai.py
│   └── requirements.txt
└── frontend/
    └── index.html
```

### 技术栈新增

- **后端**：Python 3.11 + FastAPI 0.115
- **数据库**：PostgreSQL 16（Docker 容器 `aiworld-db`）
- **ORM**：SQLAlchemy 2.0
- **认证**：JWT（python-jose + bcrypt），7 天有效期
- **AI 代理**：httpx 异步 SSE 转发，API key 移至后端 `.env`
- **环境**：conda `aiworld`（克隆自 langgraph，位于 `D:\anaconda3\envs\aiworld`）

### 接口清单

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/register` | 注册新用户 |
| POST | `/auth/login` | 登录，返回 JWT token |
| GET  | `/auth/me` | 查询当前登录用户 |
| POST | `/game/saves` | 创建存档 |
| GET  | `/game/saves` | 列出所有存档（按更新时间降序）|
| GET  | `/game/saves/{id}` | 读取存档详情 |
| PUT  | `/game/saves/{id}` | 更新存档 |
| DELETE | `/game/saves/{id}` | 删除存档 |
| POST | `/ai/chat` | 代理 Qwen SSE 流式请求 |

### 数据表

- `users`：id / username / email / password_hash / created_at
- `game_saves`：id / user_id / save_name / world_bg / char_name / char_bg / hp / max_hp / stats(JSON) / gold / turn / items(JSON) / history(JSON) / created_at / updated_at

---

## v0.4 · 前端接入后端

**日期：** 2026-05-11

### 改动内容

**认证界面**
- 新增 `#auth-panel`：登录/注册双 Tab 切换，Enter 键提交
- 登录成功后 header 显示用户名与退出按钮
- token 存 localStorage，刷新页面自动恢复登录状态（`/auth/me` 验证）

**AI 代理接入**
- `callGM` 不再直连 Qwen，改为 `POST /ai/chat`，API key 已移至后端 `.env`
- 请求携带 JWT token，未登录时自动拦截

**存读档系统**
- 每回合结束后自动调用 `autoSave()`，首次创建存档，后续更新同一条记录
- 手动点击"存档"按钮，可修改存档名后保存
- 存档模态框列出所有存档，显示角色名、回合数、最后更新时间
- "读取"按钮恢复完整游戏状态（属性/背包/历史记录），AI 自动回顾场景续写
- "删除"按钮删除单条存档
- 右下角显示"已存档 HH:MM"提示

---

## v0.5 · 工程质量提升

**日期：** 2026-05-11

### config.py 集中配置

- 新增 `config.py`，统一管理所有环境变量，缺少必填项启动即报错
- `database.py` / `security.py` / `routers/ai.py` 均改为从 config 导入，消除散落的 `os.getenv`
- 新增 `APP_ENV`（development / production）和 `ALLOWED_ORIGINS` 配置项

### Alembic 数据库迁移

- 初始化 alembic，`alembic/env.py` 自动读取 config.DATABASE_URL 和模型元数据
- 生成初始迁移 `beea2774dd4e_initial_schema`，对现有库执行 `stamp head`
- `main.py` 启动时通过 lifespan 自动执行 `alembic upgrade head`，移除 `create_all`
- 后续改表只需：`alembic revision --autogenerate -m "描述"` + `alembic upgrade head`

### CORS 按环境收窄

- `APP_ENV=development` 时 CORS 允许所有来源
- `APP_ENV=production` 时仅允许 `ALLOWED_ORIGINS` 中配置的域名

### 前端 Token 过期处理

- `apiFetch` 遇到 401 响应时自动清除 token、跳回登录界面
- 新增全局 toast 通知组件，过期提示、存档错误等均通过 toast 显示

---

## v0.6 · Structured Output + RAG

**日期：** 2026-05-11

### Structured Output

- 重构 GM system prompt，改为 `<<<JSON>>>...<<<END>>>` 分隔块格式
- `getVisible()` 截断至 `<<<JSON>>>` 前，保留打字动画效果
- 新增 `parseStructuredResponse()` 解析 JSON 块，替代正则匹配
- 新增 `applyCommands()` 统一处理数值变化（HP/GOLD/属性/道具），废弃旧的 `parseGMCommands()`
- AI 返回结构：`{"choices":[...], "commands":{"HP":0, "GOLD":0, "ITEMS_ADD":[], ...}}`

### RAG（pgvector）

- 切换容器至 `pgvector/pgvector:pg16`，数据卷 `aiworld-pgdata` 持久化
- Alembic 迁移 `2b62a7fa768c` 自动执行 `CREATE EXTENSION IF NOT EXISTS vector`，创建 `world_facts` 表（含 1024 维向量列）
- 新增 `embedding.py`：调用 DashScope `text-embedding-v3`，返回 1024 维 float 向量
- 新增 `routers/facts.py`：`POST /game/saves/{id}/facts` 存储叙事事实，内部实现 pgvector cosine 相似度检索
- `routers/ai.py` 接收 `save_id`，每次 GM 调用前检索 top-5 相关事实注入 system prompt（`【世界记忆·相关事实】`节）
- 前端 `finishNarrative()` 结束后调用 `storeFact(narrative)`，`callGM` 传入当前 `save_id`

---

## v0.7 · Docker 部署

**日期：** 2026-05-11

### 容器化方案

三容器架构，`docker compose up -d` 一键启动：

```
db (pgvector/pgvector:pg16)  ←健康检查→  backend (python:3.11-slim)
                                                    ↑
                              nginx:alpine ←代理/静态→ 端口 8080
```

### 文件变更

**`backend/Dockerfile`**
- `python:3.11-slim` 基础镜像，安装 `gcc libpq-dev`
- `pip install -r requirements.txt` → `uvicorn main:app --host 0.0.0.0 --port 8000`

**`docker-compose.yml`**
- `db`：`pgvector/pgvector:pg16`，数据卷 `pgdata` 持久化，healthcheck pg_isready
- `backend`：`env_file: ./backend/.env`，`DATABASE_URL` 环境变量覆盖为 `db:5432`（容器内网）
- `nginx`：监听 `8080:80`，挂载 `nginx/nginx.conf` 与 `frontend/`
- `DB_PASSWORD` 通过根目录 `.env` 注入

**`nginx/nginx.conf`**
- `upstream backend { server backend:8000; }`
- `/auth/`、`/game/`、`/ai/` → `proxy_pass http://backend`（`/ai/` 额外禁用缓冲支持 SSE）
- `/` → `try_files $uri $uri/ /index.html`（SPA 路由兼容）
- 预留 HTTPS/SSL 注释配置块

**`backend/main.py`**
- `StaticFiles` 改为条件挂载：目录不存在时（Docker 环境）跳过，本地开发不受影响

**`backend/requirements.txt`**
- 新增 `pgvector==0.3.6`（此前只在本地 conda 安装，Dockerfile 中缺失）

**`.gitignore`**
- 排除 `.env`、`__pycache__`、`.pytest_cache`、`pgdata/`、IDE 文件等

**`backend/.env.example` / `.env.example`**
- 生产配置模板，含 JWT_SECRET 生成命令和 ALLOWED_ORIGINS 说明

### 验证结果

```
$ docker compose ps
ai-world-game-backend-1   Up   8000/tcp
ai-world-game-db-1        Up   5432/tcp (healthy)
ai-world-game-nginx-1     Up   0.0.0.0:8080->80/tcp

GET  http://localhost:8080       → 200  (前端 HTML, 57KB)
GET  http://localhost:8080/auth/me → 401 {"detail":"Not authenticated"}
```

---

## v0.8 · 游客登录

**日期：** 2026-05-12

### 改动内容

**游客模式（无需注册即可试玩）**

- 认证面板新增"游客体验 · 无需登录"按钮（分隔线 + 低调样式）
- 点击后直接进入世界构建面板，header 显示"游客"
- 游客模式下：`autoSave` / `storeFact` 静默跳过，点"存档"弹提示"请登录后使用存档功能"
- AI 对话不携带 Authorization header，后端对未认证游客正常提供服务

**后端 `/ai/chat` 改为可选认证**

- `security.py` 新增 `get_optional_user`（`auto_error=False`），无 token 时返回 `None` 而非 401
- `routers/ai.py` 改用 `get_optional_user`，游客同样可以调用 GM，仅跳过 RAG 事实注入（无 save_id）

---

## v0.9 · 系统精简

**日期：** 2026-05-12

### 移除内容

- **骰子判定**：移除 D20 判定、属性检定关键词匹配、骰子动画与侧边栏骰子框；行动结果改由 GM 自由裁量
- **金币系统**：移除金币显示、GOLD 指令、存读档中的 gold 字段
- **背包系统**：移除道具列表、ITEM 指令、侧边栏背包框、相关 CSS

### 保留内容

HP 血条、四属性（力量/智慧/魅力/敏捷）、回合数、事件日志、存读档

### System Prompt 简化

commands JSON 从 `{HP,GOLD,STR,INT,CHA,AGI,ITEMS_ADD,ITEMS_REMOVE}` 缩减为 `{HP,STR,INT,CHA,AGI}`

---

## v0.10 · 游戏体验完善

**日期：** 2026-05-12

### 死亡结局画面
- HP 归零触发 `showDeathScreen()`，显示全屏结局遮罩（红色边框、角色名+回合数）
- 两个选项：「以同一世界重新开始」（保留世界/角色背景、重置属性HP）、「返回世界构建」
- `restartSameWorld()` 保留 `gs.tone` 和世界设定，直接开新局

### GM 叙事风格
- 世界构建面板新增「叙事风格」选项：黑暗压抑 / 轻松冒险 / 诡异悬疑 / 史诗壮阔
- 选中高亮（`.tone-btn.active`），默认黑暗压抑
- `TONES` 字典注入 system prompt `【叙事风格】` 节

### 历史记忆压缩
- `finishNarrative()` 检测 `gs.history.length > 28` 时触发 `compressHistory()`
- 把旧消息静默发给 AI 总结为 3-5 句，存入 `gs.summary`，history 修剪至最近 14 条
- system prompt 注入 `【早期剧情摘要】` 保持长局连贯性

### 存档内容预览
- 存档列表渲染时从 `s.history` 取最后一条 assistant 消息，截取前 60 字作为预览
- 新增 `.save-item-preview` 样式（省略号截断）

### 导出故事
- 游戏面板新增「导出」按钮，调用 `exportStory()`
- 把 `gs.history` 叙事文本格式化为纯文本，下载为 `{角色名}-第N回合.txt`

---

## v0.12 · 访问统计

**日期：** 2026-05-12

### 后端：访问记录接口

- 新增 `backend/routers/stats.py`，两个接口：
  - `POST /stats/visit`：记录一次页面访问（写入 `page_visits` 表）
  - `GET /stats/`：返回总访问量、今日访问量、最近 7 天每日明细
- 新增 `page_visits` 表（id UUID + created_at TIMESTAMPTZ），Alembic 迁移 `a1b2c3d4e5f6`
- nginx 新增 `location /stats/` 代理规则

### 前端：静默上报 + 显示

- `DOMContentLoaded` 时静默 POST `/stats/visit`（`.catch(() => {})` 失败不报错）
- 同时拉取 `GET /stats/` 将 `累计访问 N 次 · 今日 N 次` 显示在标题下方（低透明度，不抢眼）

### 数据库端口开放

- `docker-compose.yml` 为 db 服务新增 `ports: 5433:5432`
- 便于外部数据库客户端连接查看数据（宿主机用 5433，避免与本机 PostgreSQL 冲突）

---

## v0.11 · 文生图

**日期：** 2026-05-12

### 后端：wanx 图像接口

- 新增 `backend/routers/image.py`，`POST /ai/image`
- 使用 DashScope `wanx2.1-t2i-turbo` 异步任务模式（`X-DashScope-Async: enable`）
- 每 3 秒轮询任务状态，最多等待 75 秒，成功返回 `{"url": "..."}`
- 输出分辨率固定 `1024×576`（横幅比例，适合故事场景）

### 前端：并行生成，消除等待感

- `callGM()` 启动后立即在故事区插入 shimmer 占位块（`.story-img-placeholder`）
- `fetchImage()` 与 SSE 流并行触发（不 await），不阻塞叙事渲染
- 等叙事文本累积超 60 字后，取前 150 字作为图像提示词
- 叙事风格映射到图像风格：`dark→黑暗写实 / adventure→奇幻插画 / mystery→诡异氛围 / epic→史诗壮阔`
- 图片加载完毕后无缝替换占位块（`img.onload`），视觉过渡自然
- 图片生成失败/超时静默处理，不影响主流程

---
