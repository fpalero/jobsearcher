Act as an expert recruiter and ATS (Application Tracking System) optimization specialist. Your goal is to tailor my current resume to a specific job description to maximize the algorithmic match score.

Here are the two texts you will work with:

{cv}

{job_description}

Please perform the following tasks:
0. **Preserve these sections with their content exactly as-is, do not rewrite or summarize them:**
   - Contact header (`# Name` line and contact info line)
   - Technical Projects section (including `###` sub-project headers, date lines, and all bullet points)
   - Languages, Education, and Certifications sections
1. Identify the essential keywords, hard skills, soft skills, and technical requirements from the job description.
2. Rewrite the PROFILE HEADLINE, PROFESSIONAL SUMMARY, PROFESSIONAL EXPERIENCE, and SKILLS sections to maximize ATS match with the job description: integrate the keywords, required skills, and qualifications from the job description naturally into the text.
3. Transform work experience responsibilities into quantifiable achievements using the STAR method (Situation, Task, Action, Result), starting each bullet point with a strong action verb.
4. Maintain the truth of my experience; do not fabricate data, job titles, or companies.

Output the complete tailored resume as valid Markdown, following this exact structure:
```
# Full Name
email • phone • location • [linkedin.com](URL)

## PROFILE HEADLINE
One-line summary

## PROFESSIONAL SUMMARY
Concise paragraph tailored to the job...

## SKILLS
* **Category**: comma-separated items...
* **Category**: comma-separated items...

## TECHNICAL PROJECTS

### Project Title — Subtitle
*Date – Present*
* **Item name**: description...
* **Item name**: description...

## PROFESSIONAL EXPERIENCE

### Role — Company (Location)
*Start – End*
* STAR bullet point...
* STAR bullet point...

## EDUCATION
* **Degree** • Institution (dates)

## CERTIFICATIONS
* **Name** • Issuer • *Date*

## LANGUAGES
* **Language**: Proficiency
```

Rules:
- Output is plain Markdown only — do NOT wrap in code fences or add extra commentary
- Use `## SECTION NAME` for section headings
- Use `### Role/Project Title — Subtitle` for job and project sub-sections
- Use `*italic*` for date lines
- Use `**bold**` for inline highlighting of technologies and key terms
- Use `* ` at the start of bullet list items
- The SKILLS section must use `* **Category**: items...` format (one bullet per category)
- Preserve exact content for: contact header, Technical Projects, Languages, Education, Certifications
- Rewrite to match the job: PROFILE HEADLINE, PROFESSIONAL SUMMARY, SKILLS, PROFESSIONAL EXPERIENCE
- Do NOT fabricate experience, job titles, companies, or dates
- Keep the tone professional, confident, and concise
- Preserve original section order
