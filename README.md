# Net Template Manager

网络配置模板版本管理系统，用于管理网络设备配置模板的创建、版本控制、发布和 GitHub 同步。

## 功能特性

- **模板管理** — 创建、编辑、归档网络配置模板，支持分类组织
- **语义化版本控制** — 自动递增版本号（major/minor/patch），记录每次变更
- **版本差异对比** — 基于内容哈希检测变更，生成 diff 摘要
- **发布管理** — 将多个模板快照打包为 Release，支持 Changelog 编写
- **GitHub 集成** — 模板内容推送至 GitHub 仓库，Release 自动创建 Tag 和 GitHub Release
- **API Key 认证** — 轻量级 API 密钥鉴权，保护接口安全

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.10+, FastAPI, SQLAlchemy 2, Alembic, PyGithub |
| 前端 | Vue 3, TypeScript, Element Plus, Pinia, Monaco Editor, Vite |
| 数据库 | SQLite（默认），支持通过 `DATABASE_URL` 切换 |

## 项目结构

```
net-template-manager/
├── backend/
│   ├── alembic/              # 数据库迁移
│   ├── data/                 # SQLite 数据文件目录
│   ├── src/ntm/
│   │   ├── api/v1/           # REST API 路由（categories, templates, releases, github, system）
│   │   ├── core/             # 配置、数据库、安全
│   │   ├── models/           # SQLAlchemy 数据模型
│   │   ├── schemas/          # Pydantic 请求/响应模型
│   │   ├── services/         # 业务逻辑层
│   │   └── utils/            # 版本号计算、diff 工具
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios API 调用封装
│   │   ├── components/       # 布局组件
│   │   ├── router/           # Vue Router 路由配置
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── types/            # TypeScript 类型定义
│   │   └── views/            # 页面视图
│   └── package.json
├── .env.example
└── .gitignore
```

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，至少填写 `GITHUB_TOKEN` 和 `GITHUB_REPO`：

```env
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO=owner/repo-name
GITHUB_BRANCH=main
API_KEY=your-api-key-here
DATABASE_URL=sqlite:///./data/ntm.db
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
```

### 2. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
python -m ntm.main
```

后端运行在 `http://localhost:8000`，API 文档访问 `http://localhost:8000/docs`。

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`，已配置开发代理将 `/api` 请求转发至后端。

## API 概览

所有接口前缀 `/api/v1`，需在请求头携带 `X-API-Key`。

| 模块 | 接口 | 说明 |
|------|------|------|
| Categories | `GET/POST /categories` | 分类列表 / 创建分类 |
| Templates | `GET/POST /templates` | 模板列表（分页、筛选）/ 创建模板 |
| | `GET/PATCH/DELETE /templates/{id}` | 模板详情 / 更新 / 归档 |
| | `POST /templates/{id}/versions` | 创建新版本 |
| | `GET /templates/{id}/versions` | 版本历史列表 |
| Releases | `GET/POST /releases` | 发布列表 / 创建发布 |
| | `GET/PATCH /releases/{id}` | 发布详情 / 更新 |
| | `POST /releases/{id}/publish` | 发布到 GitHub（Tag + Release） |
| GitHub | `GET /github/test` | 测试 GitHub 连接 |
| | `GET /github/repo` | 获取仓库信息 |
| | `GET /github/commits` | 同步最近提交记录 |
| System | `GET /system/health` | 健康检查 |

## 版本号规则

遵循 [SemVer](https://semver.org/) 语义化版本：

- **major** — 不兼容的变更，递增主版本号（x.0.0）
- **minor** — 向后兼容的功能新增，递增次版本号（0.x.0）
- **patch** — 向后兼容的问题修复，递增修订号（0.0.x）

首次创建版本时，major 起始为 `1.0.0`，minor 为 `0.1.0`，patch 为 `0.0.1`。

## 数据库迁移

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## License

MIT
