import time
from application.service.applicable_service import process_applicable
from application.service.technology_service import process_technologies
from application.service.match_service import process_matches
from core.data_unified_repository import unified_jobs_collection


def pending_count() -> tuple[int, int, int]:
    a = unified_jobs_collection.count_documents({
        "$or": [{"processed": {"$ne": True}}, {"processed": {"$exists": False}}]
    })
    t = unified_jobs_collection.count_documents({
        "applicable": True,
        "$or": [
            {"technologies": {"$exists": False}},
            {"technologies": {"$eq": []}},
            {"technologies": None},
        ],
    })
    m = unified_jobs_collection.count_documents({
        "technologies": {"$exists": True, "$ne": [], "$ne": None},
        "$or": [
            {"match": {"$exists": False}},
            {"match": None},
        ],
    })
    return a, t, m


round_num = 1
while True:
    a_pending, t_pending, m_pending = pending_count()
    if a_pending == 0 and t_pending == 0 and m_pending == 0:
        print(f"\n{'=' * 50}")
        print("All docs processed!")
        print(f"{'=' * 50}")
        break

    print(f"\n{'=' * 50}")
    print(f"Round {round_num}")
    print(f"Pending — applicable: {a_pending}, technologies: {t_pending}, match: {m_pending}")
    print(f"{'=' * 50}")

    if a_pending > 0:
        print("--- Applicable ---")
        a_ok, a_err = process_applicable(batch_size=50)
        print(f"  -> {a_ok} ok, {a_err} errors")
        time.sleep(1)

    if t_pending > 0:
        print("--- Technologies ---")
        t_ok, t_err = process_technologies(batch_size=50)
        print(f"  -> {t_ok} ok, {t_err} errors")
        time.sleep(1)

    if m_pending > 0:
        print("--- Match ---")
        m_ok, m_err = process_matches(batch_size=100)
        print(f"  -> {m_ok} ok, {m_err} errors")
        time.sleep(1)

    round_num += 1

a_total = unified_jobs_collection.count_documents({"applicable": True})
print(f"\nFinal applicable count: {a_total}")
