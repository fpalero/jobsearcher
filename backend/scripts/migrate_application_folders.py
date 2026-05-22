"""Migrate resources/applications/ folders to {company_slug}-{job_id} format.

Old structure:  applications/{ambiguous folder}/CV-Company.md + company_description.md
New structure:  applications/{slug}-{job_id}/cv_{slug}-{job_id}.md + {slug}-{job_id}_description.md + pdf/
"""

import re
import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.data_unified_repository import unified_jobs_collection

BASE = Path(__file__).resolve().parent.parent / "resources" / "applications"
ORPHAN_DIR = BASE / "_orphaned"


def _slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s-]+", "_", s)
    return s.strip("_")


def _company_from_header(desc_path: Path) -> str | None:
    """Extract company name from the description file header line `**Company:** ...`."""
    if not desc_path.exists():
        return None
    for line in desc_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("**Company:**"):
            return line.split("**Company:**", 1)[1].strip()
    return None


def _company_from_folder(name: str) -> str:
    """Extract company name from old-style folder like 'Hirequill - Senior AI Engineer'."""
    parts = name.split(" - ", 1)
    return parts[0].strip()


def _find_best_job(company: str, desc_path: Path) -> list[dict]:
    """Find jobs in DB for this company. Returns list of matching job dicts."""
    jobs = list(unified_jobs_collection.find(
        {"company": {"$regex": re.escape(company), "$options": "i"}},
        {"job_id": 1, "title": 1, "company": 1},
    ))
    if not jobs:
        # Try exact after slugify
        slug = _slugify(company)
        all_companies = unified_jobs_collection.distinct("company")
        for c in all_companies:
            if _slugify(c) == slug:
                jobs = list(unified_jobs_collection.find(
                    {"company": c},
                    {"job_id": 1, "title": 1, "company": 1},
                ))
                break
    return jobs


def _match_by_description(desc_path: Path, jobs: list[dict]) -> dict | None:
    """Try to match a single job by comparing description file content with job title."""
    if not desc_path.exists() or len(jobs) == 1:
        return jobs[0] if jobs else None

    desc_text = desc_path.read_text(encoding="utf-8").lower()

    # Score each job title against the description file
    best = None
    best_score = 0
    for job in jobs:
        title = job.get("title", "").lower()
        # Count how many significant words from the title appear in the description
        words = {w for w in re.findall(r"[a-z]+", title) if len(w) > 2 and w not in {"the", "and", "for", "with", "remote"}}
        if not words:
            continue
        score = sum(1 for w in words if w in desc_text) / len(words)
        if score > best_score:
            best_score = score
            best = job

    if best and best_score >= 0.3:
        return best
    return jobs[0] if jobs else None


def migrate():
    old_folders = sorted(d for d in BASE.iterdir() if d.is_dir())
    created = 0
    skipped = 0
    orphaned = 0

    print(f"Found {len(old_folders)} folders to migrate\n")

    for folder in old_folders:
        name = folder.name

        # Find description file inside folder
        desc_in_folder = list(folder.glob("*_description.md"))
        desc_candidates = [f for f in desc_in_folder if f.is_file()]

        # Also check for a _description.md with the folder name pattern
        if not desc_candidates:
            desc_candidates = list(folder.glob("*.md"))
            desc_candidates = [f for f in desc_candidates if "_description" in f.name]

        desc_path = desc_candidates[0] if desc_candidates else None

        # Extract company name
        company = None
        if desc_path:
            company = _company_from_header(desc_path)
        if not company:
            company = _company_from_folder(name)

        jobs = _find_best_job(company, desc_path) if company else []

        if not jobs:
            print(f"  ORPHAN: '{name}' — no matching job in DB, deleting")
            shutil.rmtree(folder)
            orphaned += 1
            continue

        matched = _match_by_description(desc_path, jobs)

        if not matched:
            print(f"  SKIP: '{name}' — could not match any job among {len(jobs)}")
            skipped += 1
            continue

        job_id = matched["job_id"]
        # Ensure unique job_id for matching
        if isinstance(job_id, list):
            job_id = job_id[0]

        slug = f"{_slugify(company)}-{job_id}"
        new_dir = BASE / slug

        if new_dir.exists():
            print(f"  SKIP: '{name}' → {slug} (already exists)")
            skipped += 1
            continue

        new_dir.mkdir(parents=True)

        # Copy CV file
        cv_candidates = []
        for f in folder.iterdir():
            if f.is_file() and f.name.lower().startswith("cv") and f.suffix == ".md":
                cv_candidates.append(f)
        if cv_candidates:
            cv_src = cv_candidates[0]
            cv_dst = new_dir / f"cv_{slug}.md"
            shutil.copy2(cv_src, cv_dst)

        # Copy description file
        if desc_path:
            desc_dst = new_dir / f"{slug}_description.md"
            shutil.copy2(desc_path, desc_dst)

        # Copy any PDF
        pdf_candidates = [f for f in folder.iterdir() if f.suffix == ".pdf"]
        if pdf_candidates:
            pdf_dir = new_dir / "pdf"
            pdf_dir.mkdir(exist_ok=True)
            for pdf_src in pdf_candidates:
                pdf_dst = pdf_dir / f"cv_{slug}.pdf"
                shutil.copy2(pdf_src, pdf_dst)

        # Remove old folder
        shutil.rmtree(folder)
        print(f"  OK: '{name}' → {slug}/")
        created += 1

    print(f"\nDone. Created: {created}, Skipped: {skipped}, Orphaned/deleted: {orphaned}")


if __name__ == "__main__":
    migrate()
