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
    'software engineer', 'senior', 'go', 'gcp',
}

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


def skill_in_cv(skill: str) -> bool:
    skill_lower = skill.lower().strip()
    if skill_lower in CV_SKILLS:
        return True
    mapped = TECH_TO_CV_SKILL.get(skill_lower)
    if mapped and mapped in CV_SKILLS:
        return True
    return False


def compute_match(technologies: list[str]) -> int:
    if not technologies:
        return 0
    matched = sum(1 for tech in technologies if skill_in_cv(tech))
    total = max(len(technologies), 1)
    score = int((matched / total) * 100)
    return max(min(score, 100), 0)


def process_matches(batch_size: int = 100) -> tuple[int, int]:
    query = {
        "technologies": {"$exists": True, "$ne": [], "$ne": None},
        "$or": [
            {"match": {"$exists": False}},
            {"match": None},
        ],
    }
    total = unified_jobs_collection.count_documents(query)
    processed = 0
    errors = 0

    cursor = unified_jobs_collection.find(query).limit(batch_size).batch_size(batch_size)

    for doc in cursor:
        try:
            technologies = doc.get("technologies") or []
            score = compute_match(technologies)
            unified_jobs_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"match": score}}
            )
            processed += 1

        except Exception as e:
            print(f"  [ERROR] match: {doc.get('title', '?')[:50]} → {e}")
            errors += 1

    print(f"  match: {processed} ok, {errors} errors (total pending: {total})")
    return processed, errors
