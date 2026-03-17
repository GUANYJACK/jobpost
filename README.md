# Job Application Automation System

## 项目简介
自动化职位申请流程，支持网页爬取、简历与求职信智能生成、应用状态追踪。

## 快速开始

### 1. 环境依赖
- Python 3.8+
- pip install fastapi sqlmodel uvicorn requests beautifulsoup4

### 2. 启动服务
```
uvicorn app.main:app --reload
```

### 3. API使用
- POST /scrape/  
  参数：url（职位页面链接）
- GET /applications/  
  返回所有已抓取职位

### 4. 数据库
- 默认使用SQLite（jobpost.db）

## 后续开发
- 集成LLM智能简历排序与求职信生成
- 前端页面与Dashboard
- 状态追踪与应用详情页

## 配置说明
- 后续将支持API Key、数据库切换等配置

---
如需进一步功能或有反馈，请直接提出。
