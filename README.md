# JobPost — 职位申请自动化系统

> 一个基于 FastAPI 的职位爬取与求职流程管理工具，支持职位信息抓取、简历上传预览、AI 简历优化以及申请状态跟踪。

---

## 📦 项目结构概览

- `app/` - 后端业务逻辑
  - `main.py` - FastAPI 应用入口与路由
  - `models.py` - 数据模型（职位、简历）
  - `database.py` - SQLite + SQLModel 初始化与会话管理
  - `scraper.py` - 职位详情爬虫与解析逻辑
  - `resume_*` - 简历上传、解析、AI 调整逻辑
- `app/templates/` - Jinja2 页面模板（首页、详情、简历页等）
- `static/` - 静态文件（已上传的简历、示例文档等）
- `jobpost.db` - 默认 SQLite 数据库文件（自动生成）

---

## 🚀 快速启动

### 1. 安装依赖
推荐使用虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

> 如果还没有 `requirements.txt`，你可以手动安装：
> `pip install fastapi uvicorn sqlmodel requests beautifulsoup4 python-docx PyPDF2 fpdf`


### 2. 启动开发服务器

```powershell
uvicorn app.main:app --reload
```

浏览器访问：

```
http://127.0.0.1:8000/
```

---

## 🧩 主要功能概览

### ✅ 职位爬取与管理
- 支持通过「职位链接」提取职位标题、公司、薪资、地点、JD 文本等
- 支持查看职位详情和标记申请/未申请状态
- 已抓取的职位会存入本地 SQLite（`jobpost.db`）

### ✅ 简历上传与预览
- 上传 `.docx` / `.pdf` 简历文件
- 提取简历文本并保存到数据库
- 通过前端页面直接预览已上传简历

### ✅ AI 简历优化（可选）
- 集成 Google Gemini（需要设置环境变量 `GEMINI_API_KEY`）
- 通过 AI 重新生成/优化简历文本

---

## 🔌 关键路由说明

### 页面 (Web UI)
- `/` - 首页：职位列表 + 抓取入口
- `/detail/{app_id}` - 职位详情页
- `/resume` - 简历管理与 AI 调整页
- `/resume_list` - 简历历史列表

### API 接口（保留兼容）
- `POST /scrape/` - 通过 `url` 抓取职位（返回 JSON）
- `GET /applications/` - 列出所有职位（返回 JSON）

### 重要表单路由
- `POST /submit_url` - 提交职位链接进行抓取
- `POST /upload_resume` - 上传简历文件
- `POST /ai_adjust_resume` - AI 优化简历
- `POST /save_resume` - 保存当前简历文本
- `POST /mark_applied/{app_id}` - 标记已申请
- `POST /mark_unapplied/{app_id}` - 标记为未申请

---

## ⚙ 配置与环境变量

- `GEMINI_API_KEY`：用于调用 Google Gemini 的 API Key（可选）

---

## 🧪 开发/调试小贴士

- 若修改了模板或静态资源，请重启 `uvicorn`（`--reload` 应该会自动生效）
- SQLite 数据库文件位于根目录 `jobpost.db`，可使用 SQLite 浏览器查看

---

如需添加新功能（例如：登录系统、任务提醒、邮件通知、职位标签）我可以继续帮你规划和实现。