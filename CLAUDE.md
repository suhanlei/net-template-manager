# CLAUDE.md — Net Template Manager 项目指令

## 项目概述
Net Template Manager（NTM）是网络配置模板版本管理系统，后端 FastAPI + SQLAlchemy，前端 Vue 3 + Element Plus + Pinia。配置模板文件存放在 `templates/` 目录下，按厂商/层级分类。

## 技术栈
- 后端：Python 3.10+, FastAPI, SQLAlchemy 2, Alembic, PyGithub, SQLite
- 前端：Vue 3, TypeScript, Element Plus, Pinia, Vite, Axios

## 开发启动
```bash
# 后端
cd backend && .venv/Scripts/activate && python -m ntm.main   # http://localhost:8000

# 前端
cd frontend && npm run dev   # http://localhost:5173（代理 /api -> :8000）
```

## 配置
- 后端配置在 `backend/.env`，参考 `.env.example`
- GitHub Token 和仓库信息必须配置才能使用 Commit/Publish 功能
- GITHUB_BRANCH 默认为 master
- 模板 GitHub Path 必须以 `templates/` 开头，如 `templates/H3C/CORE/S12500_base.cfg`

## 代码结构
- `backend/src/ntm/api/v1/` — API 路由，按资源分文件（categories, templates, releases, github, system）
- `backend/src/ntm/services/` — 业务逻辑，不直接暴露数据库细节
- `backend/src/ntm/models/` — SQLAlchemy ORM 模型
- `backend/src/ntm/schemas/` — Pydantic 请求/响应 schema
- `frontend/src/views/` — 页面组件（Dashboard, TemplateList, TemplateDetail, ReleaseList, ReleaseDetail, Settings）
- `frontend/src/stores/` — Pinia 状态管理（category, template, release）
- `frontend/src/api/modules.ts` — 所有 API 调用封装

## 重要约定
- 模板删除是归档（status -> archived），不是物理删除
- 版本状态流转：draft -> committed
- Release 状态流转：draft -> published（不可逆）
- 版本号遵循 SemVer：major/minor/patch 自动递增
- 前端模板列表默认只显示 active 状态
- SQLAlchemy echo 已关闭（echo=True 会触发热重载导致数据丢失）

## API 认证
- 后端定义了 `verify_api_key` 依赖（`core/security.py`），但当前路由未挂载
- 请求头格式：`X-API-Key: <key>`
- 默认 API Key：`ntm-dev-key`

## 数据库迁移
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Git 规范
- 用户：suhanlei <531492914@qq.com>
- 远程：https://github.com/suhanlei/net-template-manager.git
- 默认分支：master
