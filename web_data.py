import re
import requests
from bs4 import BeautifulSoup
from classes import linkClass
from links import RemoteLinks

# edit this dictionary to add subjects, set year limits, or isolate components.
# do not touch the loops below; they read this map dynamically.
FILTER_CONFIG = {
    # igcse math: keep extended (papers 2 & 4), drop core (1 & 3), limit to 2020+
    "0580": {
        "min_year": 2020,
        "exclude_regex": r"_(qp|ms|er|in|ci|qr|rp)_(1|3)\d"
    },
    # igcse physics: keep extended (2 & 4), drop core (1 & 3), limit to 2020+
    "0625": {
        "min_year": 2020,
        "exclude_regex": r"_(qp|ms|er|in|ci|qr|rp)_(1|3)\d"
    },
    # as computer science: keep as (1 & 2), drop a2 (3 & 4), limit to 2021+
    "9618": {
        "min_year": 2021,
        "exclude_regex": r"_(qp|ms|er|in|ci|sf|qr|rp)_(3|4)\d"
    },
    # igcse esl: keep modern format, limit to 2021+
    "0510": {
        "min_year": 2021,
        "exclude_regex": None
    }
}

def getExamClasses(url, pattern):
    '''
    gets separate classes filtered strictly by subject codes.
    '''
    print(f'fetching exam links from: {url}')
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    page = requests.get(url, headers=headers).text
    soup = BeautifulSoup(page, "lxml")
    exams = []
    
    code_pattern = re.compile(r'\b\d{3,4}\b')
    
    for a in soup.find_all('a', href=True):
        link = a['href']
        name = a.text.strip()
        
        if name.lower() in ['home', 'parent directory', '..', ''] or not name:
            continue
            
        if "papafy" in link.lower() or "ai" in name.lower() or "javascript" in link.lower():
            continue
            
        if code_pattern.search(name) and ('-' in name or '(' in name):
            if not link.startswith('http'):
                link = RemoteLinks.PAST_PAPERS.value + link.lstrip('/')

            if str(pattern).isdigit():
                if str(pattern) in name:
                    print(f"target matched: {name}")
                    exams.append(linkClass(name, link))
            else:
                exams.append(linkClass(name, link))

    print('finished downloading exam links')
    return exams

def getExamSeasons(url):
    '''
    gets seasons and filters dynamically by year limit in config.
    '''
    print('fetching exam seasons...')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    page = requests.get(url, headers=headers).text
    soup = BeautifulSoup(page, "html.parser")
    examSeasons = []
    
    year_pattern = re.compile(r'\b(20\d{2}|19\d{2})\b')
    
    # check if the active url contains any of our configured subject keys
    min_year = 0
    for code, config in FILTER_CONFIG.items():
        if code in url:
            min_year = config.get("min_year", 0)
            break
            
    for a in soup.find_all('a', href=True):
        name = a.text.strip()
        link = a['href']
        
        if name.lower() in ['home', 'parent directory', '..', ''] or not name:
            continue
            
        if "papafy" in link.lower() or "ai" in name.lower() or "javascript" in link.lower() or "board=" in link:
            continue
            
        if year_pattern.search(name) or "topical" in name.lower():
            year_match = year_pattern.search(name)
            if year_match:
                year_num = int(year_match.group(1))
                # drop old years to save disk space
                if min_year > 0 and year_num < min_year:
                    continue
            
            if not link.startswith('http'):
                link = RemoteLinks.PAST_PAPERS.value + link.lstrip('/')
                
            examSeasons.append(linkClass(name, link))
            print(f'fetching season folder: {name}')

    return examSeasons

def getExams(url):
    '''
    gets individual exams and filters using declarative exclude regex.
    '''
    print('fetching individual exams...')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    page = requests.get(url, headers=headers).text
    soup = BeautifulSoup(page, "html.parser")
    exams = []
    
    code_match = re.search(r'\b\d{3,4}\b', url)
    subject_code = code_match.group(0) if code_match else ""
    
    for a in soup.find_all('a', href=True):
        name = a.text.strip()
        link = a['href']
        
        if name.lower() in ['home', 'parent directory', '..', ''] or not name:
            continue
            
        if "papafy" in link.lower() or "ai" in name.lower() or "javascript" in link.lower():
            continue
            
        examName = link.split('/')[-1] if '/' in link else name
        
        if any(examName.lower().endswith(ext) for ext in ['.pdf', '.txt', '.doc', '.docx', '.zip', '.png', '.jpg']):
            
            # check if we have a config mapped for this subject
            if subject_code in FILTER_CONFIG:
                config = FILTER_CONFIG[subject_code]
                
                # 1. spam blocker: drop files belonging to other subjects
                if not examName.startswith(subject_code):
                    continue
                
                # 2. components filter: apply custom regex if declared
                exclude_pattern = config.get("exclude_regex")
                if exclude_pattern and re.search(exclude_pattern, examName.lower()):
                    continue
            
            if not link.startswith('http'):
                link = RemoteLinks.PAST_PAPERS.value + link.lstrip('/')
                
            print(f'fetching url for asset: {examName}')
            exams.append(linkClass(examName, link))
        
    return exams