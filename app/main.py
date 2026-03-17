



from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from app.models import Application
from app.database import init_db, get_session
from app.scraper import scrape_job_post
from app.resume_model import Resume
from app.resume_utils import extract_text_from_file
import requests
import os
from fastapi import UploadFile

from fastapi.staticfiles import StaticFiles
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

@app.on_event("startup")
def on_startup():
    init_db()

# 前端主页
# 前端主页
@app.get("/", response_class=HTMLResponse)
def index(request: Request, sort: str = "desc"):
    """主页：按提交时间排序（默认降序）。

    sort 参数：
    - asc: 旧的先（升序）
    - desc: 新的先（降序）
    """
    with get_session() as session:
        query = select(Application)
        if sort == "asc":
            query = query.order_by(Application.id)
        else:
            query = query.order_by(Application.id.desc())
        apps = session.exec(query).all()
    return templates.TemplateResponse("index.html", {"request": request, "applications": apps, "sort": sort})


# 新增简历页面
@app.get("/resume", response_class=HTMLResponse)
def resume_page(request: Request, id: int = None):
    with get_session() as session:
        resume = None
        resume_objs = session.exec(select(Resume)).all()
        resume_list = []
        for r in resume_objs:
            resume_list.append({
                'id': r.id,
                'file_path': r.file_path,
                'file_url': f"/static/{os.path.basename(r.file_path)}" if r.file_path else None,
                'resume_text': r.resume_text,
                'updated_at': r.updated_at.strftime('%Y-%m-%d %H:%M:%S') if r.updated_at else '未知',
                'original_filename': r.original_filename or '未知文件名'
            })
        if id:
            resume = session.get(Resume, id)
        else:
            resume = session.exec(select(Resume)).first()
        resume_text = resume.resume_text if resume else ""
        prompt = "请优化以下简历内容，使其更适合求职："
        resume_file_url = None
        if resume and hasattr(resume, 'file_path') and resume.file_path:
            resume_file_url = f"/static/{os.path.basename(resume.file_path)}"
    return templates.TemplateResponse("resume.html", {"request": request, "resume_text": resume_text, "prompt": prompt, "resume_file_url": resume_file_url, "resume_list": resume_list})

# 上传简历文件
@app.post("/upload_resume", response_class=HTMLResponse)
async def upload_resume(request: Request, resume_file: UploadFile):
    ext = os.path.splitext(resume_file.filename)[1].lower()
    save_dir = "static"
    os.makedirs(save_dir, exist_ok=True)
    # 用时间戳+原文件名防止覆盖
    import time
    timestamp = int(time.time())
    save_path = os.path.join(save_dir, f"resume_{timestamp}_{resume_file.filename}")
    content = await resume_file.read()
    with open(save_path, "wb") as f:
        f.write(content)
    resume_text = extract_text_from_file(save_path)
    pdf_path = None
    if ext == ".docx":
        from app.docx2pdf_utils import docx_to_pdf
        pdf_path = save_path.replace(".docx", ".pdf")
        try:
            docx_to_pdf(save_path, pdf_path)
        except Exception as e:
            pdf_path = None
    from datetime import datetime
    with get_session() as session:
        new_resume = Resume(
            resume_text=resume_text,
            file_path=pdf_path if pdf_path else save_path,
            original_filename=resume_file.filename,
            updated_at=datetime.now()
        )
        session.add(new_resume)
        session.commit()
    return RedirectResponse("/resume", status_code=303)

# AI智能调整简历（POST，支持自定义prompt）
@app.post("/ai_adjust_resume", response_class=HTMLResponse)
async def ai_adjust_resume(request: Request, prompt: str = Form(...)):
    with get_session() as session:
        resume = session.exec(select(Resume)).first()
        if not resume or not resume.resume_text:
            return templates.TemplateResponse("resume.html", {"request": request, "resume_text": "", "error": "请先上传简历", "prompt": prompt})
        full_prompt = f"{prompt}\n{resume.resume_text}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}
        }
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            ai_text = result['candidates'][0]['content']['parts'][0]['text'] if 'candidates' in result else "AI调整失败"
            resume.adjusted_text = ai_text
            session.add(resume)
            session.commit()
            return templates.TemplateResponse("resume.html", {"request": request, "resume_text": ai_text, "prompt": prompt})
        else:
            return templates.TemplateResponse("resume.html", {"request": request, "resume_text": resume.resume_text, "error": "AI调整失败", "prompt": prompt})

# 保存简历
@app.post("/save_resume", response_class=HTMLResponse)
def save_resume(request: Request, resume: str = Form(...)):
    with get_session() as session:
        old_resume = session.exec(select(Resume)).first()
        if old_resume:
            old_resume.resume_text = resume
            session.add(old_resume)
            session.commit()
        else:
            new_resume = Resume(resume_text=resume)
            session.add(new_resume)
            session.commit()
    return RedirectResponse("/resume", status_code=303)

# AI智能调整简历
@app.get("/ai_adjust_resume", response_class=HTMLResponse)
def ai_adjust_resume(request: Request):
    with get_session() as session:
        resume = session.exec(select(Resume)).first()
        if not resume or not resume.resume_text:
            return templates.TemplateResponse("resume.html", {"request": request, "resume_text": "", "error": "请先上传简历"})
        prompt = f"请优化以下简历内容，使其更适合求职：\n{resume.resume_text}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}
        }
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            ai_text = result['candidates'][0]['content']['parts'][0]['text'] if 'candidates' in result else "AI调整失败"
            resume.adjusted_text = ai_text
            session.add(resume)
            session.commit()
            return templates.TemplateResponse("resume.html", {"request": request, "resume_text": ai_text})
        else:
            return templates.TemplateResponse("resume.html", {"request": request, "resume_text": resume.resume_text, "error": "AI调整失败"})

# URL提交表单处理
@app.post("/submit_url", response_class=HTMLResponse)
def submit_url(request: Request, url: str = Form(...)):
    with get_session() as session:
        # 如果已存在相同 URL，则不重复新增，直接提示用户
        existing = session.exec(select(Application).where(Application.url == url)).first()
        if existing:
            apps = session.exec(select(Application).order_by(Application.id.desc())).all()
            return templates.TemplateResponse("index.html", {"request": request, "applications": apps, "error": "该岗位已存在，无法重复添加"})

    data = scrape_job_post(url)
    print(f"[DEBUG] 爬取结果: {data}")
    if not data['job_title'] or not data['jd_text']:
        with get_session() as session:
            apps = session.exec(select(Application)).all()
            print(f"[DEBUG] 提取失败，当前数据库职位数: {len(apps)}")
        return templates.TemplateResponse("index.html", {"request": request, "applications": apps, "error": "无法提取职位信息"})
    app_obj = Application(
        url=url,
        job_title=data['job_title'],
        company_name=data['company_name'],
        salary=data.get('salary'),
        location=data.get('location'),
        compensation=data.get('compensation'),
        jd_text=data['jd_text'],
        status="Scraped"
    )
    with get_session() as session:
        session.add(app_obj)
        session.commit()
        session.refresh(app_obj)
        print(f"[DEBUG] 新增职位: {app_obj.id}, {app_obj.job_title}, {app_obj.company_name}, {app_obj.salary}, {app_obj.location}, {app_obj.compensation}, {app_obj.status}")
    return RedirectResponse("/", status_code=303)

# 详情页
@app.get("/detail/{app_id}", response_class=HTMLResponse)
def detail(request: Request, app_id: int):
    with get_session() as session:
        app_obj = session.get(Application, app_id)
    if not app_obj:
        return HTMLResponse("<h2>未找到该职位</h2>", status_code=404)
    return templates.TemplateResponse("detail.html", {"request": request, "app": app_obj})


# 保留API接口
@app.post("/scrape/")
def scrape_and_save(url: str):
    data = scrape_job_post(url)
    if not data['job_title'] or not data['jd_text']:
        raise HTTPException(status_code=400, detail="无法提取职位信息")
    app_obj = Application(
        url=url,
        job_title=data['job_title'],
        company_name=data['company_name'],
        salary=data.get('salary'),
        location=data.get('location'),
        compensation=data.get('compensation'),
        jd_text=data['jd_text'],
        status="Scraped"
    )
    with get_session() as session:
        session.add(app_obj)
        session.commit()
        session.refresh(app_obj)
    return app_obj

@app.get("/applications/")
def list_applications():
    with get_session() as session:
        apps = session.exec(select(Application)).all()
    return apps


@app.post("/mark_applied/{app_id}", response_class=HTMLResponse)
def mark_applied(request: Request, app_id: int):
    with get_session() as session:
        app_obj = session.get(Application, app_id)
        if not app_obj:
            return HTMLResponse("<h2>未找到该职位</h2>", status_code=404)
        app_obj.status = "Applied"
        session.add(app_obj)
        session.commit()
        session.refresh(app_obj)
    return RedirectResponse(f"/detail/{app_id}", status_code=303)

@app.post("/mark_unapplied/{app_id}", response_class=HTMLResponse)
def mark_unapplied(request: Request, app_id: int):
    with get_session() as session:
        app_obj = session.get(Application, app_id)
        if not app_obj:
            return HTMLResponse("<h2>未找到该职位</h2>", status_code=404)
        app_obj.status = "Scraped"
        session.add(app_obj)
        session.commit()
        session.refresh(app_obj)
    return RedirectResponse(f"/detail/{app_id}", status_code=303)

# 简历列表页面
@app.get("/resume_list", response_class=HTMLResponse)
def resume_list(request: Request):
    with get_session() as session:
        resumes = session.exec(select(Resume)).all()
    # 构造文件url
    for r in resumes:
        r.file_url = f"/static/{os.path.basename(r.file_path)}" if r.file_path else None
    return templates.TemplateResponse("resume_list.html", {"request": request, "resumes": resumes})