# 水库日常巡查记录系统

面向水库管理单位的轻量级巡查与隐患闭环管理系统：维护水库台账，按次录入日常巡查记录，
登记巡查发现的隐患，并跟踪整改、验收、销号全过程。

- 后端：FastAPI + SQLAlchemy 2.0 + Pydantic v2，分层为 `api / services / models / schemas`
- 前端：Vue 3 + Vite + Pinia + Vue Router，按业务模块拆分视图与组件，非单页堆砌
- 部署：`docker-compose` 一键启动（PostgreSQL + FastAPI + nginx 托管前端静态资源）

## 功能模块

| 模块 | 说明 |
| --- | --- |
| 总览 | 水库 / 巡查 / 隐患统计，隐患状态与等级分布，逾期隐患待办、最近巡查列表 |
| 水库台账 | 水库工程信息增删改查，支持按行政区、运行状态、大坝安全类别筛选，列表直接展示最近巡查时间与未销号隐患数 |
| 巡查记录 | 按“巡查主表 + 巡查项明细”录入，逐部位记录检查结果；存在异常项时自动判定结论为「发现异常」并引导登记隐患 |
| 隐患登记 | 隐患标题、类别、等级、来源、发现日期、整改期限、责任人、整改方案，可关联来源巡查记录 |
| 整改跟踪 | 整改状态机流转 + 整改流水（措施 / 进展 / 验收 / 销号），逾期自动标记 |

## 目录结构

```
.
├── backend/                     # FastAPI 服务
│   ├── app/
│   │   ├── api/v1/endpoints/    # 按业务模块拆分的路由：reservoirs / inspections / hazards / overview / meta
│   │   ├── core/                # 配置与领域异常
│   │   ├── db/                  # 引擎、会话、基类、演示数据
│   │   ├── models/              # ORM 模型与枚举（enums.py 同时维护中文标签）
│   │   ├── schemas/             # 出入参校验与序列化
│   │   ├── services/            # 业务逻辑（含隐患状态机，可脱离 HTTP 单独测试）
│   │   └── main.py              # 应用装配
│   ├── tests/                   # pytest 接口测试（30 个用例）
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                    # Vue 3 单页应用
│   ├── src/
│   │   ├── api/                 # 按后端模块封装的请求方法
│   │   ├── components/          # 通用组件 + 各业务模块组件（reservoir / inspection / hazard）
│   │   ├── composables/         # 列表筛选与 URL 同步等复用逻辑
│   │   ├── layouts/             # 应用框架布局
│   │   ├── router/              # 路由表（按模块懒加载）
│   │   ├── stores/              # Pinia：字典、提示、确认弹窗
│   │   ├── styles/              # 设计令牌与全局样式
│   │   ├── utils/               # 格式化与表单清洗
│   │   └── views/               # 页面：dashboard / reservoir / inspection / hazard
│   ├── Dockerfile               # 多阶段构建：node 构建 + nginx 托管
│   └── nginx.conf
├── docker-compose.yml
└── .env.example
```

## 快速开始

### 方式一：docker compose（推荐）

```bash
cp .env.example .env          # Windows: copy .env.example .env
docker compose up -d --build
```

启动后：

| 地址 | 说明 |
| --- | --- |
| http://localhost:8080 | 前端页面（nginx） |
| http://localhost:8000/api/v1/meta/health | 后端健康检查 |
| http://localhost:8000/docs | 后端接口文档（Swagger UI） |

首次启动会自动建表并灌入演示数据（7 座水库、12 条巡查记录、8 条隐患）。已有数据时不会重复灌入；
如需全新空库，执行 `docker compose down -v` 后重新启动。

常用命令：

```bash
docker compose ps            # 查看服务状态
docker compose logs -f backend
docker compose down          # 停止（保留数据卷）
docker compose down -v       # 停止并删除数据库数据卷
```

### 方式二：本地开发

后端（默认使用 SQLite，文件位于 `backend/data/reservoir.db`）：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173 ，/api 自动代理到 127.0.0.1:8000
```

> 若浏览器访问不了 `http://localhost:5173`，可用 `npm run dev -- --host 0.0.0.0` 让开发服务器监听全部网卡。

## 业务规则

**巡查结论自动判定**：巡查记录本身不手工填写结论，只要有一项巡查项结果为「异常」，整条记录的结论即为
「发现异常」，避免人为漏判。编辑巡查项后结论会重新计算。

**隐患整改状态机**（`backend/app/services/hazard_service.py`）：

```
待整改(registered)
  ├─ 开始整改 ─────────────> 整改中(rectifying)
  └─ 直接销号(需填写说明) ──> 已销号(closed)

整改中(rectifying)
  ├─ 提交验收(需填写说明) ──> 待验收(pending_acceptance)
  └─ 直接销号(需填写说明) ──> 已销号(closed)

待验收(pending_acceptance)
  ├─ 验收通过并销号 ────────> 已销号(closed)
  └─ 验收不通过(需填写说明) ─> 整改中(rectifying)

已销号(closed)  终态
```

- 状态只能通过 `POST /api/v1/hazards/{id}/transition` 变更，每次流转都会写入整改流水（含变更前后状态），
  用 `PUT` 直接改状态会被拒绝（HTTP 422）。
- 非法流转（例如从「待整改」直接跳到「待验收」）返回 HTTP 409。
- 追加「整改措施」类型的记录时，隐患会自动从「待整改」进入「整改中」。
- 已销号隐患不能再追加整改记录，也不提供任何流转入口。

**逾期判定**：存在整改期限且未销号，且当前日期已超过期限，即视为逾期；列表支持 `overdue_only=true`
只筛逾期隐患，总览页单独统计逾期数量。

**删除保护**：水库下存在巡查或隐患记录时不允许删除（返回 422 并提示先清理关联数据）；巡查记录被隐患
引用时不允许删除。隐患删除会级联删除其整改流水，操作前有二次确认。

**时间口径**：系统面向单一时区部署，单据日期、编号流水、逾期判断统一使用服务器本地时间，
容器内通过 `TZ=Asia/Shanghai` 固定时区。

## 数据模型

| 表 | 说明 | 关键关系 |
| --- | --- | --- |
| `reservoir` | 水库台账（编码唯一） | 1:N 巡查、隐患 |
| `inspection` | 巡查记录主表（编号唯一，结论由明细推导） | N:1 水库；1:N 巡查项 |
| `inspection_item` | 巡查项明细（部位、结果、说明） | N:1 巡查记录 |
| `hazard` | 隐患台账（编号唯一，含状态、等级、期限、销号日期） | N:1 水库；N:1 来源巡查（可空） |
| `hazard_rectification` | 整改跟踪流水（类型、内容、记录人、状态变更） | N:1 隐患 |

字典（运行状态、坝型、安全类别、隐患等级、状态等）统一在后端 `app/models/enums.py` 维护，
由 `GET /api/v1/meta/options` 下发，前端不再重复硬编码中文标签。

## 接口一览

基础路径 `/api/v1`，完整参数与响应模型见 `http://localhost:8000/docs`。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/meta/options` | 全部下拉字典、已有行政区、隐患状态机 |
| GET | `/meta/health` | 健康检查（含数据库连通性） |
| GET | `/overview/summary` | 总览统计、待办隐患、最近巡查 |
| GET/POST | `/reservoirs` | 水库台账分页查询 / 新增 |
| GET/PUT/DELETE | `/reservoirs/{id}` | 水库详情 / 更新 / 删除 |
| GET | `/reservoirs/{id}/stats` | 单库巡查与隐患统计 |
| GET/POST | `/inspections` | 巡查记录分页查询 / 新增（含巡查项） |
| GET/PUT/DELETE | `/inspections/{id}` | 巡查详情 / 更新（可整体替换巡查项）/ 删除 |
| GET/POST | `/hazards` | 隐患台账分页查询 / 登记 |
| GET/PUT/DELETE | `/hazards/{id}` | 隐患详情（含整改流水）/ 更新 / 删除 |
| POST | `/hazards/{id}/rectifications` | 追加整改跟踪记录 |
| POST | `/hazards/{id}/transition` | 整改状态流转 |

列表接口统一支持 `page` / `page_size`，返回 `{items, total, page, page_size, pages}`。

## 配置项

后端环境变量（`backend/app/core/config.py`）：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite+pysqlite:///./data/reservoir.db` | 数据库连接串，PostgreSQL 用 `postgresql+psycopg://...` |
| `API_PREFIX` | `/api/v1` | 接口前缀 |
| `SEED_DEMO_DATA` | `true` | 空库时是否灌入演示数据 |
| `CORS_ORIGINS` | `*` | 逗号分隔的允许来源 |
| `SQL_ECHO` | `false` | 是否打印 SQL |
| `DEFAULT_PAGE_SIZE` / `MAX_PAGE_SIZE` | `20` / `100` | 分页默认与上限 |

compose 的端口、数据库口令等项在根目录 `.env`（从 `.env.example` 复制）中覆盖：`WEB_PORT`（前端，默认 8080）、`BACKEND_PORT`（后端，默认 8000）、`TZ`（时区，默认 Asia/Shanghai）。8080 被占用时改 `WEB_PORT` 即可。
前端环境变量见 `frontend/.env.example`：`VITE_API_BASE_URL`（默认 `/api/v1`，由代理转发）、`VITE_PROXY_TARGET`（本地开发时 /api 代理目标，默认 `http://127.0.0.1:8000`）。

## 测试与自检

```bash
cd backend
python -m pytest            # 30 个接口用例：台账 CRUD、编号生成、巡查结论推导、状态机、逾期、统计
```

```bash
cd frontend
npm run build               # 生产构建（顺带校验所有组件与路由）
npm run preview             # 预览构建产物（同样把 /api 代理到后端）
```

## 说明

- 建表方式为启动时 `create_all`，未引入迁移框架；表结构变更后需要重建库或自行引入 Alembic。
- 演示数据用于快速体验，生产部署请设置 `SEED_DEMO_DATA=false`。
- 前端交互使用统一的提示与确认弹窗组件，接口错误直接展示后端返回的中文 `detail`。
