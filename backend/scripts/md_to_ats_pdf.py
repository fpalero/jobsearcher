import argparse
import os
import re
import tempfile
from pathlib import Path
from unicodedata import normalize

import typst

UNICODE_ASCII = {
    "\u2013": "-",     "\u2014": "--",    "\u2015": "--",
    "\u2018": "'",     "\u2019": "'",     "\u201a": "'",
    "\u201b": "'",     "\u201c": '"',     "\u201d": '"',
    "\u201e": '"',     "\u2022": "-",     "\u2026": "...",
    "\u2032": "'",     "\u2033": '"',     "\u00a0": " ",
    "\u00ab": '"',     "\u00bb": '"',     "\u00b7": "*",
}

RESOURCES = Path(__file__).resolve().parent.parent / "resources"
TEMPLATE_PATH = RESOURCES / "pdf" / "cv_template.typ"


def normalize_text(text: str) -> str:
    text = normalize("NFKC", text)
    for char, replacement in UNICODE_ASCII.items():
        text = text.replace(char, replacement)
    return text


def esc(text: str) -> str:
    return normalize_text(text).replace('"', '\\"')

def esc_text(text: str) -> str:
    text = normalize_text(text)
    text = text.replace("\\", "\\\\")
    text = text.replace("#", "\\#")
    text = text.replace("$", "\\$")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    text = text.replace("[", "\\[")
    text = text.replace("]", "\\]")
    return text


def _gen_typst_value(val, inner: str) -> str:
    if isinstance(val, tuple):
        vals = ",\n".join(f'{inner}  "{esc(str(v))}"' for v in val if v)
        return f"(\n{vals},\n{inner})"
    return f'"{esc(str(val))}"'


def _gen_typst_tuples(items: list[tuple], fields: list[str], indent: int = 4) -> str:
    pad = " " * indent
    inner = " " * (indent + 2)
    if not items:
        return "()"
    entries: list[str] = []
    for item in items:
        kvs_list: list[str] = []
        for field, val in zip(fields, item):
            if field == "url" and not val:
                kvs_list.append(f'{inner}{field}: "#"')
            elif isinstance(val, tuple):
                val_str = _gen_typst_value(val, inner) if val else "()"
                kvs_list.append(f'{inner}{field}: {val_str}')
            else:
                kvs_list.append(f'{inner}{field}: "{esc(str(val))}"')
        kvs = ",\n".join(kvs_list)
        entries.append(f"{pad}(\n{kvs},\n{pad})")
    return f"(\n{',\n'.join(entries)},\n{' ' * (indent - 2)})"


def _extract_works(experiences: list[dict]) -> list[tuple]:
    works: list[tuple] = []
    for exp in experiences:
        dates = exp.get("dates", "").split(" - ")
        start = dates[0].strip() if dates else ""
        end = dates[1].strip() if len(dates) > 1 else ""
        achievements = tuple(exp.get("achievements", []))
        works.append((
            exp.get("company", ""),
            exp.get("location", ""),
            "#",
            "",
            exp.get("role", ""),
            start,
            end,
            achievements,
        ))
    return works


def _extract_skills_dict(skills: dict) -> list[tuple]:
    items: list[tuple[str, str]] = []
    for category, text in skills.items():
        items.append((category, normalize_text(text)))
    return items


def _parse_multiline_items(text: str) -> list[str]:
    items: list[str] = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^[\*\-\•]\s*", "", line)
        items.append(line)
    return items


def _parse_contact_str(contact_str: str) -> dict:
    lines = contact_str.strip().split("\n")
    result: dict[str, str] = {}
    name_line = lines[0].replace("## ", "").strip() if lines else ""
    result["name"] = name_line
    if len(lines) > 1:
        parts = [p.strip() for p in lines[1].split("|")]
        result["email"] = parts[0] if len(parts) > 0 else ""
        result["phone"] = parts[1] if len(parts) > 1 else ""
        result["location"] = parts[2] if len(parts) > 2 else ""
        for p in parts:
            if "linkedin" in p.lower():
                result["linkedin"] = p.split(":", 1)[-1].strip() if ":" in p else p
                break
        if "linkedin" not in result:
            result["linkedin"] = ""
    return result


def _normalize_contact(data: dict) -> dict:
    contact_val = data.get("contact", "")
    if isinstance(contact_val, dict):
        return contact_val
    return _parse_contact_str(str(contact_val))


def _normalize_skills(data: dict) -> str:
    skills_val = data.get("skills", "")
    if isinstance(skills_val, dict):
        items = []
        for cat, txt in skills_val.items():
            cat = cat.strip()
            txt = txt.strip()
            if not cat and not txt:
                continue
            items.append(f"{cat}: {txt}" if cat else txt)
        return "\n".join(items)
    return str(skills_val)


def _stripped(val: str) -> str:
    raw = re.sub(r"^##\s*", "", str(val))
    raw = re.sub(r"\*\*(.+?)\*\*", r"\1", raw)
    raw = re.sub(r"^[\*\-\•]\s*", "", raw, flags=re.MULTILINE)
    return raw.strip()


def _normalize_education_entries(data: dict) -> list[tuple]:
    val = data.get("education", "")
    if isinstance(val, list):
        entries: list[tuple] = []
        for item in val:
            if isinstance(item, dict):
                entries.append((
                    item.get("institution", ""),
                    item.get("location", ""),
                    "",
                    "",
                    item.get("degree", ""),
                    item.get("start_date", ""),
                    item.get("end_date", ""),
                    item.get("gpa", ""),
                    (),
                ))
        if entries:
            return entries
    lines = _parse_multiline_items(_stripped(str(val)))
    return [(l, "", "", "", "", "", "", "", ()) for l in lines]


def _normalize_cert_entries(data: dict) -> list[tuple]:
    val = data.get("certifications", "")
    if isinstance(val, list):
        entries: list[tuple] = []
        for item in val:
            if isinstance(item, dict):
                date = item.get("date", "")
                date = re.sub(r"(?i)^issued\s*", "", date).strip()
                entries.append((
                    item.get("name", ""),
                    item.get("issuer", ""),
                    "",
                    date,
                ))
        if entries:
            return entries
    lines = _parse_multiline_items(_stripped(str(val)))
    return [(l, "", "", "") for l in lines]


def _render_projects(data: dict) -> str:
    val = data.get("technical_projects", "")
    out: list[str] = ["= Technical Projects"]
    if isinstance(val, list):
        for proj in val:
            if not isinstance(proj, dict):
                continue
            name = proj.get("name", "").strip()
            desc = proj.get("description", "").strip()
            if name:
                out.append(f"=== {esc_text(name)}")
            if desc:
                for p in desc.split("\n"):
                    p = p.strip()
                    if not p:
                        continue
                    if re.match(r'^[A-Z][a-z]+ \d{4}\s*[-–]\s*(Present|\d{4})$', p):
                        continue
                    out.append(f"- {esc_text(p)}")
                out.append("")
    else:
        text = _stripped(str(val))
        if text:
            for p in text.split("\n"):
                p = p.strip()
                if not p:
                    continue
                if re.match(r'^[A-Z][a-z]+ \d{4}\s*[-–]\s*(Present|\d{4})$', p):
                    continue
                out.append(f"- {esc_text(p)}")
                out.append("")
    return "\n".join(out)


def _render_skills(data: dict) -> str:
    skills_val = data.get("skills", "")
    out: list[str] = ["= Skills"]
    if isinstance(skills_val, dict):
        for cat, txt in skills_val.items():
            cat = cat.strip()
            txt = txt.strip()
            if not cat and not txt:
                continue
            if cat:
                out.append(f"- #text(weight: \"bold\")[{esc_text(cat)}]: {esc_text(txt)}")
            else:
                out.append(f"- {esc_text(txt)}")
    else:
        text = _stripped(str(skills_val))
        if text:
            for line in text.split("\n"):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(":", 1)
                if len(parts) == 2 and parts[0].strip():
                    out.append(f"- #text(weight: \"bold\")[{esc_text(parts[0].strip())}]: {esc_text(parts[1].strip())}")
                else:
                    out.append(f"- {esc_text(line)}")
    out.append("")
    return "\n".join(out)


def _render_education(data: dict) -> str:
    entries = _normalize_education_entries(data)
    out: list[str] = ["= Education"]
    if entries:
        for entry in entries:
            inst, loc, _, _, degree, start_date, end_date, score, _ = entry
            parts = []
            if degree:
                parts.append(f"#text(weight: \"bold\")[{esc_text(degree)}]")
            elif inst:
                parts.append(f"#text(weight: \"bold\")[{esc_text(inst)}]")
            if inst and degree:
                parts.append(esc_text(inst))
            if loc:
                parts.append(esc_text(loc))
            dates = []
            if start_date:
                dates.append(esc_text(start_date))
            if end_date:
                dates.append(esc_text(end_date))
            if dates:
                parts.append(" — ".join(dates))
            if score:
                parts.append(score)
            out.append(f"- {' | '.join(parts)}")
            out.append("")
    return "\n".join(out)


def _render_certifications(data: dict) -> str:
    entries = _normalize_cert_entries(data)
    out: list[str] = ["= Certifications"]
    if entries:
        for entry in entries:
            name, issuer, _, date = entry
            parts = [name, issuer]
            if date:
                parts.append(date)
            out.append(esc_text(" — ".join(p for p in parts if p)))
            out.append("")
    return "\n".join(out)


def _render_section(title: str, body: str) -> str:
    lines: list[str] = []
    lines.append(f"= {esc_text(title)}")
    for paragraph in body.strip().split("\n\n"):
        paragraph = paragraph.strip()
        if paragraph:
            lines.extend(esc_text(paragraph).split("\n"))
            lines.append("")
    return "\n".join(lines)


def construir_codigo_typst(data: dict) -> str:
    resume = data.get("resume", data)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    contact = _normalize_contact(resume)

    split_marker = "#let render_font"
    idx = template.find(split_marker)
    if idx == -1:
        base_import = '#import "@preview/fantastic-cv:0.1.0": *\n\n'
        render_config = ""
    else:
        base_import = template[: template.find("\n") + 1]
        render_config = template[template.find(split_marker):]

    out: list[str] = []
    out.append(base_import)
    out.append("\n")

    name = esc(contact.get("name", ""))
    email = esc(contact.get("email", ""))
    phone = esc(contact.get("phone", ""))
    location = esc(contact.get("location", ""))
    linkedin_url = esc(contact.get("linkedin", ""))
    out.append(f'#let name = "{name}"\n')
    out.append(f'#let location = "{location}"\n')
    out.append(f'#let email = "{email}"\n')
    out.append(f'#let phone = "{phone}"\n')
    out.append(f'#let url = "{linkedin_url or "#"}"\n')

    if linkedin_url and linkedin_url != "#":
        username = linkedin_url.rstrip("/").split("/")[-1]
        out.append(f'#let profiles = (\n    (network: "LinkedIn", username: "{esc(username)}", url: "{linkedin_url}"),\n  )\n')
    else:
        out.append("#let profiles = ()\n")

    experiences = resume.get("professional_experience", [])
    works = _extract_works(experiences) if isinstance(experiences, list) else []
    works_fields = ["name", "location", "url", "description", "position", "startDate", "endDate", "highlights"]
    out.append(f"#let works = {_gen_typst_tuples(works, works_fields)}\n")

    edu_entries = _normalize_education_entries(resume)
    out.append("#let educations = ()\n")

    cert_entries = _normalize_cert_entries(resume)
    cert_fields = ["name", "issuer", "url", "date"]
    out.append(f"#let certificates = {_gen_typst_tuples(cert_entries, cert_fields)}\n")

    out.append("#let projects = ()\n")
    out.append("#let volunteers = ()\n")
    out.append("#let awards = ()\n")
    out.append("#let publications = ()\n")
    out.append("#let programming_language_section = (title: \"\", highlights: ())\n")
    out.append("#let skills_section = (title: \"\", highlights: ())\n")

    summary = _stripped(resume.get("professional_summary", ""))
    headline = _stripped(resume.get("profile_headline", ""))

    render_before: list[str] = []
    if edu_entries:
        render_before.append(_render_education(resume))
    if headline:
        render_before.append(_render_section("Profile", headline))
    if summary:
        render_before.append(_render_section("Professional Summary", summary))
    if resume.get("skills"):
        render_before.append(_render_skills(resume))
    if resume.get("technical_projects"):
        render_before.append(_render_projects(resume))

    render_after: list[str] = []
    languages_text = resume.get("languages", "")
    if isinstance(languages_text, str) and languages_text.strip():
        lang_items = _parse_multiline_items(languages_text)
        if lang_items:
            lines = ["= Languages"]
            for item in lang_items:
                if ":" in item:
                    name, rest = item.split(":", 1)
                    lines.append(f"- #text(weight: \"bold\")[{esc_text(name.strip())}]:{esc_text(rest.strip())}")
                else:
                    lines.append(f"- {esc_text(item)}")
            render_after.append("\n".join(lines))
        else:
            render_after.append(_render_section("Languages", languages_text.strip()))

    out.append("\n")
    out.append(render_config)

    work_marker = "#render-work(works)"
    work_idx = render_config.find(work_marker)
    if work_idx >= 0 and (render_before or render_after):
        before_config = render_config[:work_idx]
        after_config = render_config[work_idx:]
        combined = before_config + "\n"
        if render_before:
            combined += "\n".join(render_before) + "\n"
        combined += after_config + "\n"
        if render_after:
            combined += "\n".join(render_after) + "\n"
        out.pop()
        out.append(combined)
    else:
        if render_before:
            out.append("\n".join(render_before) + "\n")
        if render_after:
            out.append("\n".join(render_after) + "\n")

    return "\n".join(out)


def cv_json_to_pdf(json_data: dict, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    typst_code = construir_codigo_typst(json_data)

    tmp = tempfile.NamedTemporaryFile(suffix=".typ", mode="w", delete=False, encoding="utf-8")
    try:
        tmp.write(typst_code)
        tmp.close()
        typst.compile(tmp.name, output=str(pdf_path))
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)


_MD_REPLACEMENTS = [
    (r"^###\s*(.+)", r"=== \1"),
    (r"^##\s*(.+)", r"== \1"),
    (r"^#\s*(.+)", r"= \1"),
    (r"\*\*(.+?)\*\*", r"*\1*"),
    (r"(?m)^- ", r"- "),
]


def _escape_typst_markup(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace("#", "\\#")
    text = text.replace("$", "\\$")
    text = text.replace("@", "\\@")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    text = text.replace("[", "\\[")
    text = text.replace("]", "\\]")
    return text


def _md_to_typst(md_text: str) -> str:
    for pattern, replacement in _MD_REPLACEMENTS:
        md_text = re.sub(pattern, replacement, md_text)
    md_text = _escape_typst_markup(md_text)
    return normalize_text(md_text)


def md_to_ats_pdf(md_path: Path, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    content = md_path.read_text(encoding="utf-8")
    body = _md_to_typst(content)

    typst_code = f'#set page(paper: "us-letter", margin: (x: 1.5cm, y: 1.5cm))\n#set text(size: 11pt)\n#show par: set block(spacing: 0.5em)\n\n{body}\n'

    tmp = tempfile.NamedTemporaryFile(suffix=".typ", mode="w", delete=False, encoding="utf-8")
    try:
        tmp.write(typst_code)
        tmp.close()
        typst.compile(tmp.name, output=str(pdf_path))
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
