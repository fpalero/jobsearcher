import json
from langchain_core.prompts import ChatPromptTemplate
from app.core.data_unified_repository import unified_jobs_collection
from app.service.llm_config import get_llm

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """You are a technical recruiter determining if a job offer is applicable for a candidate.

A job is applicable ONLY if ALL of the following conditions are met:
1. **Remote or Germany-based**: The job is remote (`is_remote` is true), OR the location/country contains a German city or region (Berlin, Munich, Hamburg, Frankfurt, Cologne, Stuttgart, Düsseldorf, Leipzig, Dresden, Nuremberg, Hannover, Bremen, Bonn, Bavaria, North Rhine-Westphalia, Hesse, Baden-Württemberg, etc.).
2. **No geographic restrictions outside Germany**: If the description states that the remote work is restricted to a specific country or region other than Germany (e.g. "remote within the UK", "remote in the United Kingdom", "must be based in the UK", "remote within the US", "London or remote within the UK", "remote in Europe but must be UK-based"), the job is NOT applicable. If the remote work restriction includes Germany (e.g. "remote within the EU" or "remote in Europe"), it is still applicable.
3. **English language**: The job description is in English.
4. **No mandatory C1+ German**: If the job requires German language skills at C1 level or higher (e.g. "C1 German", "fluent German", "native German", "German at C1", "verhandlungssicher Deutsch", "muttersprachlich Deutsch", "Deutschkenntnisse C1"), the job is NOT applicable. A2/B1/B2 level German is acceptable.

If the description is shorter than 10 words, assume it is English and has no German requirement.

Respond in JSON format only:
{{"applicable": true/false, "reason": "short explanation"}}"""),
    ("human", "Title: {title}\nLocation: {location}\nCountry: {country}\nIs Remote: {is_remote}\n\nDescription:\n{description}"),
])


def process_applicable(batch_size: int = 50) -> tuple[int, int]:
    llm = get_llm()
    chain = PROMPT_TEMPLATE | llm

    query = {"$or": [{"processed": {"$ne": True}}, {"processed": {"$exists": False}}]}
    total = unified_jobs_collection.count_documents(query)
    processed = 0
    errors = 0

    cursor = unified_jobs_collection.find(query).limit(batch_size).batch_size(batch_size)

    for doc in cursor:
        try:
            title = doc.get("title") or doc.get("job_title") or ""
            location = doc.get("location") or doc.get("job_location") or ""
            country = doc.get("country") or doc.get("job_country") or ""
            is_remote = doc.get("is_remote") or doc.get("job_is_remote") or False
            description = (doc.get("description") or doc.get("description_text") or "")[:3000]

            response = chain.invoke({
                "title": title,
                "location": location,
                "country": country,
                "is_remote": str(is_remote),
                "description": description,
            })

            result = json.loads(response.content.strip())
            applicable = bool(result.get("applicable", False))

            unified_jobs_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "applicable": applicable,
                    "processed": True,
                    "_applicable_reason": result.get("reason", ""),
                }}
            )
            processed += 1

        except Exception as e:
            print(f"  [ERROR] applicable: {doc.get('title', '?')[:50]} → {e}")
            unified_jobs_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"processed": True, "applicable": False}}
            )
            errors += 1

    print(f"  applicable: {processed} ok, {errors} errors (total pending: {total})")
    return processed, errors
