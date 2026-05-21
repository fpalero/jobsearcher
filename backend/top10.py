from pymongo import MongoClient
import re

client = MongoClient('mongodb://midzospa:3VcdcelzsTWGNkApcA6x8PsW@localhost:27017/jobsearcher?authSource=admin')
db = client['jobsearcher']

cv_keywords = {
    'Java': 10, 'Spring Boot': 10, 'Spring Cloud': 8, 'Microservices': 10,
    'Python': 8, 'LangChain': 6, 'LLM': 7, 'AI': 8, 'AWS': 8, 'Azure': 7,
    'Cloud': 9, 'Angular': 7, 'React': 6, 'TypeScript': 7,
    'PostgreSQL': 8, 'MongoDB': 7, 'Kafka': 7, 'Docker': 9, 'Kubernetes': 5,
    'CI/CD': 8, 'DDD': 8, 'SOLID': 8, 'TDD': 8, 'Team Lead': 9, 'Mentor': 7,
    'Agile': 7, 'REST': 9, 'API': 9, 'Architect': 9,
}

def calc_match(title, desc):
    text = f'{title} {desc}'.lower()
    score = sum(w for s, w in cv_keywords.items() if s.lower() in text)
    return round(score / sum(cv_keywords.values()) * 100)

loc_res = [
    'must be based in', 'must reside in', 'local candidates only',
    'must live in', 'authorized to work in', 'right to work in',
    'philippines based', 'ph based', 'us based', 'uk based',
    'relocate to', 'on.?site in', 'located in', 'work from.*office',
    'annapolis junction', 'indianapolis', 'secret clearance'
]

jobs = list(db.unified_jobs.find({'source': 'JSearch', 'is_remote': True}))
suitable = []
for job in jobs:
    desc = (job.get('description') or '').lower()
    t = (job.get('title') or '').lower()
    combined = f'{t} {desc}'
    if any(re.search(p, combined) for p in loc_res):
        continue
    pct = calc_match(job.get('title', ''), job.get('description', ''))
    suitable.append((pct, job))

suitable.sort(key=lambda x: -x[0])

seen = set()
n = 0
print(f'{"Rank":<5} {"Match":<7} {"Company":<35} {"Title"}')
print('-' * 100)
for pct, job in suitable:
    co = job.get('company', 'Unknown')
    if co not in seen:
        seen.add(co)
        n += 1
        title = job.get('title', '')[:50]
        print(f'{n:<5} {pct}%{"":<5} {co:<35} {title}')
    if n >= 10:
        break
