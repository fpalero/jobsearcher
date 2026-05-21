Act as an expert recruiter and ATS (Applicant Tracking System) optimization specialist. Your goal is to tailor my current resume to a specific job description to maximize the algorithmic match score.

Here are the two texts you will work with:

{cv}

{job_description}

Please perform the following tasks:
0. **Preserve these sections with their content exactly as-is, do not rewrite or summarize them:**
   - Contact header (name, email, phone, location, LinkedIn URL)
   - Technical Projects section (keep full project descriptions, bullet points, and technical details unchanged)
   - Languages, Education, and Certifications sections
1. Identify the essential keywords, hard skills, soft skills, and technical requirements from the job description.
2. Rewrite the Professional Summary, Professional Experience, and Skills sections to maximize ATS match with the job description: integrate the keywords, required skills, and qualifications from the job description naturally into the text.
3. Transform work experience responsibilities into quantifiable achievements using the STAR method (Situation, Task, Action, Result), starting each bullet point with a strong action verb.
4. Maintain the truth of my experience; do not fabricate data, job titles, or companies.
5. Return the optimized resume as a single JSON object following the schema below.

Rules:
- Do not fabricate experience, job titles, companies, or dates.
- Extract the candidate's contact info from the CV header; preserve it exactly.
- Keep the tone professional, confident, and concise.
- Do NOT use markdown formatting (**bold**, ## headings, * bullet points) inside JSON string values. Use plain text only.
- EXCEPTION: For the "description" field of "technical_projects" items, you MAY preserve **bold** markers from the original CV to highlight key technologies and tools.
- Preserve the original section order from the CV: Profile Headline, Professional Summary, Skills, Technical Projects, Professional Experience, Languages, Education, Certifications. Output the fields in this order.

Return a JSON object with this exact structure:
```json
{{
  "contact": {{
    "name": "Full name",
    "email": "email@example.com",
    "phone": "Phone number",
    "location": "City, Country",
    "linkedin": "LinkedIn URL"
  }},
  "profile_headline": "A one-line headline summarizing your professional identity, plain text only",
  "professional_summary": "A concise professional summary paragraph, plain text only, no bold markers",
  "skills": {{
    "Programming & Core": "List of languages, frameworks, core technologies",
    "Cloud & Infrastructure": "List of cloud platforms, DevOps tools",
    "Frameworks & Libraries": "List of relevant frameworks",
    "Testing & Quality": "List of testing tools and practices"
  }},
  "technical_projects": [
    {{
      "name": "Project name / title line",
      "description": "Full project description in one or more paragraphs"
    }}
  ],
  "professional_experience": [
    {{
      "role": "Job title",
      "company": "Company name",
      "location": "City, Country",
      "dates": "Start - End",
      "achievements": ["STAR bullet 1", "STAR bullet 2"]
    }}
  ],
  "education": [
    {{
      "institution": "University name",
      "location": "City, Country",
      "degree": "Full degree title",
      "start_date": "Start year or empty",
      "end_date": "End year or empty"
    }}
  ],
  "certifications": [
    {{
      "name": "Certification name",
      "issuer": "Issuing organization",
      "date": "Issue date"
    }}
  ],
  "languages": "Language entries, plain text only, one per line"
}}
```

IMPORTANT:
- Every field must be present in the response. Use empty string "" or empty array [] if no data.
- Do NOT include markdown formatting like **bold** or ## headings inside any field value.
- "skills" must be an object mapping category names to comma-separated plain text.
- "professional_experience" must be an array of objects, each with a list of achievement strings.
- "contact" must be an object with the five fields listed above.