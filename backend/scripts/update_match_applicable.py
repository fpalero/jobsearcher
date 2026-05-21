import sys
import re
sys.path.insert(0, '.')
from core.data_unified_repository import unified_jobs_collection

CV_SKILLS = {
    'java', 'spring boot', 'spring cloud', 'spring', 'microservices', 'python',
    'angular', 'react', 'typescript', 'javascript', 'docker', 'docker compose',
    'devcontainer', 'kubernetes', 'aws', 'azure', 'kafka', 'postgresql', 'mongodb',
    'rest', 'api', 'ci/cd', 'github actions', 'git', 'tdd', 'junit', 'mockito',
    'cypress', 'selenium', 'jasmine', 'karma', 'pytest', 'ddd', 'agile', 'scrum',
    'ai', 'machine learning', 'ml', 'llm', 'langchain', 'langgraph', 'llamaindex',
    'rag', 'prompt engineering', 'tensorflow', 'prisma', 'appsmith', 'nextcloud',
    'solid', 'event-driven', 'ecs', 'ec2', 's3', 'event hub', 'cosmos db',
    'full stack', 'fullstack', 'backend', 'frontend', 'cloud',
    'software engineer', 'senior',
}

CV_SENIORITY = {'senior', 'lead', 'staff', 'principal', 'architect', 'team lead'}

TECH_TO_CV_SKILL = {
    'golang': 'go',
    'k8s': 'kubernetes',
    'amazon web services': 'aws',
    'google cloud': 'gcp',
    'react native': 'react',
    'postgres': 'postgresql',
    'retrieval-augmented generation': 'rag',
    'domain-driven design': 'ddd',
    'artificial intelligence': 'ai',
}

ENGLISH_STOP_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has',
    'had', 'do', 'does', 'did', 'will', 'would', 'can', 'could', 'shall',
    'should', 'may', 'might', 'must', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her',
    'its', 'our', 'their', 'and', 'or', 'but', 'if', 'because', 'as', 'until',
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
    'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 'just', 'also', 'well', 'please', 'experience', 'work', 'team',
}

GERMANY_LOCATIONS = {'germany', 'deutschland', 'berlin', 'munich', 'münchen',
                     'hamburg', 'frankfurt', 'cologne', 'köln', 'stuttgart',
                     'düsseldorf', 'dusseldorf', 'leipzig', 'dresden',
                     'nuremberg', 'nürnberg', 'hannover', 'bremen', 'bonn',
                     'ruhr', 'bavaria', 'bayern', 'baden-württemberg',
                     'baden-wurttemberg', 'north rhine-westphalia',
                     'nrw', 'hesse', 'hessen'}


def is_english(text: str) -> bool:
    if not text:
        return True
    words = re.findall(r'[a-zA-Z]+', text.lower())
    if len(words) < 10:
        return True
    stop_count = sum(1 for w in words if w in ENGLISH_STOP_WORDS)
    ratio = stop_count / len(words)
    return ratio > 0.08


def skill_in_cv(skill: str) -> bool:
    skill_lower = skill.lower().strip()
    if skill_lower in CV_SKILLS:
        return True
    mapped = TECH_TO_CV_SKILL.get(skill_lower)
    if mapped and mapped in CV_SKILLS:
        return True
    return False


def compute_match(doc: dict) -> int:
    technologies = doc.get('technologies') or []
    title = (doc.get('title') or doc.get('job_title') or '').lower()

    if not technologies:
        description = (doc.get('description') or doc.get('description_text') or '').lower()
        role_query = (doc.get('_role_query') or doc.get('role_query') or '').lower()
        text = f'{title} {description[:2000]} {role_query}'
        matched = sum(1 for kw in CV_SKILLS if kw in text)
        if matched == 0:
            return 0
        raw = (matched / len(CV_SKILLS)) * 100
        return min(int(raw), 100)

    matched_count = sum(1 for tech in technologies if skill_in_cv(tech))
    total = max(len(technologies), 1)
    raw_score = (matched_count / total) * 100

    score = min(int(raw_score), 100)
    return max(score, 0)


def compute_applicable(doc: dict) -> bool:
    is_remote = doc.get('is_remote') or doc.get('job_is_remote') or False
    if isinstance(is_remote, str):
        is_remote = is_remote.lower() == 'true'

    location = (doc.get('location') or doc.get('job_location') or '').lower()
    country = (doc.get('country') or doc.get('job_country') or '').lower()

    is_germany_location = any(g in location or g in country for g in GERMANY_LOCATIONS)

    if not is_remote and not is_germany_location:
        return False

    description = doc.get('description') or doc.get('description_text') or ''
    if not is_english(description):
        return False

    return True


def main():
    total = unified_jobs_collection.count_documents({})
    print(f'Total documents: {total}')

    updated = 0
    for doc in unified_jobs_collection.find():
        match = compute_match(doc)
        applicable = compute_applicable(doc)
        job_id = doc.get('_id')
        title = doc.get('title') or doc.get('job_title') or '?'
        unified_jobs_collection.update_one(
            {'_id': job_id},
            {'$set': {'match': match, 'applicable': applicable}}
        )
        print(f'  [{applicable and "✓" or "✗"}] match={match:3d}  {title[:50]}')
        updated += 1

    print(f'\nUpdated {updated} documents')
    print(f'Applicable count: {unified_jobs_collection.count_documents({"applicable": True})}')


if __name__ == '__main__':
    main()
