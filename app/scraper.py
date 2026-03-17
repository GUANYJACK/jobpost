from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from sys import stdout

def countdown(seconds):
    for i in range(seconds, 0, -1):
        print(f"抓取中，倒数 {i} 秒...", end="\r", flush=True)
        time.sleep(1)
    print(" " * 30, end="\r")  # 清空行

def scrape_job_post(url: str):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    countdown(3)  # 替换原有的 time.sleep(3)
    html = driver.page_source
    print(f"[DEBUG] 页面源码长度: {len(html)}")
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    job_title = None
    company_name = None
    salary = None
    location = None
    jd_text = None

    # 岗位名称（优先data-automation='job-detail-title'）
    job_title_tag = soup.find('h1', attrs={'data-automation': 'job-detail-title'})
    if job_title_tag:
        job_title = job_title_tag.text.strip()
    else:
        job_title = soup.title.text.strip() if soup.title else None
    print(f"[DEBUG] job_title: {job_title}")

    # 公司名
    company_tag = soup.find('span', attrs={'data-automation': 'advertiser-name'})
    print(f"[DEBUG] advertiser-name节点: {company_tag}")
    if company_tag:
        company_name = company_tag.text.strip()

    # 薪水
    salary_tag = soup.find('span', attrs={'data-automation': 'job-detail-salary'})
    print(f"[DEBUG] job-detail-salary节点: {salary_tag}")
    if salary_tag:
        salary = salary_tag.text.strip()

    # 地理位置
    location_tag = soup.find('span', attrs={'data-automation': 'job-detail-location'})
    print(f"[DEBUG] job-detail-location节点: {location_tag}")
    if location_tag:
        # location可能在a标签内
        a_tag = location_tag.find('a')
        if a_tag:
            location = a_tag.text.strip()
        else:
            location = location_tag.text.strip()

    # 岗位介绍
    jd_section = soup.find('div', class_='kx2b1u0')
    print(f"[DEBUG] kx2b1u0节点: {jd_section}")
    if jd_section:
        jd_text = jd_section.get_text(separator='\n', strip=True)

    print(f"[DEBUG] 提取结果: job_title={job_title}, company_name={company_name}, salary={salary}, location={location}, jd_text_len={len(jd_text) if jd_text else 0}")

    return {
        'job_title': job_title,
        'company_name': company_name,
        'salary': salary,
        'location': location,
        'jd_text': jd_text
    }