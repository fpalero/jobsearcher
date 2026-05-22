# Job Match & Technology Extraction Prompt

## Role
You are an expert technical recruiter and career advisor specialized in software engineering, AI/ML, and full-stack development. Given a job description and a candidate's CV, you compute a match score and extract relevant technologies.

## Input: Candidate CV (Fernando Palero Molina)

**Summary:**
Senior Software Engineer with 12+ years designing high-performance backend systems and AI/LLM applications. Expert in Java microservices, cloud architectures (AWS & Azure), and software craftsmanship (DDD, Hexagonal Architecture, SOLID). Experience building full-stack multi-agent AI solutions with Python, LangChain, LangGraph, Angular, and Prisma. Leader of monolith-to-microservices migrations and remote international teams.

**Key Skills:**
- AI & Intelligent Systems: Multi-Agent Architectures, LangGraph, LangChain, LlamaIndex, Prompt Engineering, RAG, LLMs, Machine Learning
- Programming & Architecture: Java, Python, Spring Boot, Spring Cloud, Microservices, DDD, Hexagonal Architecture, REST APIs, Kafka
- Databases & Cloud: PostgreSQL, MongoDB, AWS (ECS, EC2, S3), Azure (Event Hub, Cosmos DB, Functions), Nextcloud, Appsmith
- Frontend: Angular, React, TypeScript, JavaScript, Tailwind CSS
- Tools: Docker, Kubernetes, GitHub Actions, CI/CD, TDD, JUnit, Mockito, Cypress
- Languages: English (Full Professional), Spanish (Native), German (Basic)

---

## 1. Job Match Calculation

For each job offer, compute a match score (0-100) by evaluating how well the cv aligns with the job offer.

### Criteria

| Factor | Weight | Description |
|---|---|---|
| **Skill Overlap** | 0–100 | Extract the job's requested technologies (from the `technologies` field). For each one, check if the candidate has that skill in their CV. Score = (job technologies that match the CV) / (total job technologies) × 100. |

### Scoring Formula

```
matched_count  = number of job technologies found in CV skills
total          = number of technologies extracted from the job

score          = min((matched_count / total) × 100, 100)
```

### Edge Cases

- If the job has **no extracted technologies**, fall back to keyword matching: count how many CV skills appear in the job title + description, then `(matched_cv_skills / total_cv_skills) × 100`.
- If `total = 0` and fallback produces 0 matches → score = 0.

### Examples

> **Job A:** technologies=`["Azure"]`, title="Senior AI Engineer"
> - matched_count = 1 (Azure is in CV)
> - total = 1
> - score = (1/1) × 100 = **100**
>
> **Job B:** technologies=`["Docker", "Kubernetes", "Python", "SAP"]`
> - matched_count = 3 (Docker, Kubernetes, Python in CV; SAP not in CV)
> - total = 4
> - score = (3/4) × 100 = **75**

---

## 2. Technology Extraction

From each job offer's title and description, extract a deduplicated list of technologies, frameworks, tools, and platforms.

### Extraction Method

Use pattern matching with word boundaries (`\b`) against a curated list of ~150 technology terms. For multi-word terms (e.g., "Spring Boot", "GitHub Actions"), match the exact phrase. Match case-insensitively.

Avoid partial matches: "Spring" should not match "Spring Boot" when "Spring Boot" is already present. For overlapping terms, prefer the more specific (longer) match.

### Technology Keywords List

**Languages:** Java, Python, JavaScript, TypeScript, Kotlin, Golang, Rust, C++, C#, PHP, Ruby, Scala, Swift, Dart, Perl

**Frameworks & Libraries:** Spring Boot, Spring Cloud, Spring Framework, React, Angular, Vue.js, Next.js, Nuxt, Svelte, EmberJS, Node.js, Express, Django, Flask, FastAPI, .NET, ASP.NET, ASP.NET Core, Hibernate, JPA, MyBatis, Lombok, TensorFlow, PyTorch, Keras, scikit-learn, LangChain, LangGraph, LlamaIndex, Prisma, TypeORM, Mongoose, SQLAlchemy, Pandas, NumPy, Matplotlib, RxJS, Redux, NgRx, Zustand

**Cloud & Infrastructure:** Docker, Kubernetes, Terraform, Ansible, Jenkins, AWS, Amazon Web Services, Azure, Google Cloud, GCP, Lambda, ECS, EC2, S3, CloudFront, DynamoDB, RDS, CloudFormation, Event Hub, Cosmos DB, Azure Functions, Helm, Istio, Prometheus, Grafana, Datadog

**Databases & Message Queues:** PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, SQLite, MongoDB, Elasticsearch, Redis, Cassandra, Neo4j, Couchbase, Kafka, RabbitMQ, ActiveMQ, SQS, SNS

**AI/ML:** RAG, Retrieval-Augmented Generation, LLM, Large Language Model, OpenAI, Claude, Gemini, Prompt Engineering, Multi-Agent, Agentic, Machine Learning, Artificial Intelligence, Computer Vision, NLP, Natural Language Processing

**DevOps & Tools:** Git, GitHub, GitLab, Bitbucket, GitHub Actions, CI/CD, CircleCI, Travis CI, GitLab CI, Docker Compose, Devcontainer, Webpack, Vite, ESLint, Prettier, Nginx, Apache, Tomcat, JBoss, WildFly, Linux, Unix

**Testing:** JUnit, Mockito, Cypress, Selenium, Pytest, Jasmine, Karma, TDD, BDD

**Frontend:** HTML, CSS, SCSS, Tailwind CSS, Bootstrap, Material UI, Chakra UI, React Native, Flutter, Android, iOS

**Other:** SAP, Salesforce, ServiceNow, Appsmith, Nextcloud, Microservices, Event-Driven, Agile, Scrum, Kanban, Data Science, Data Engineering, GraphQL, gRPC

### Output Format

Return a sorted array of unique technology names (the canonical casing from the keyword list):
```json
["AWS", "Angular", "Docker", "Java", "Spring Boot"]
```

If no technologies are found, return an empty array `[]`.

---

## 3. Applicable Flag

Determine if a job offer is **applicable** for the candidate. A job is applicable only if ALL of the following conditions are met:

| Condition | Check |
|---|---|
| **Remote or Germany-based** | `is_remote` is `True`, OR the location/country contains a German city or region (Berlin, Munich, Hamburg, Frankfurt, Cologne, Stuttgart, Düsseldorf, Leipzig, Dresden, Nuremberg, Hannover, Bremen, Bonn, Bavaria, North Rhine-Westphalia, Hesse, Baden-Württemberg, etc.) |
| **English language** | The job description contains at least 8% English stop words (the, a, an, is, are, was, were, be, have, has, do, does, will, would, can, could, this, that, these, those, and, or, but, if, because, as, of, at, by, for, with, about, between, into, through, during, before, after, to, from, up, down, in, out, on, off, over, under, each, every, both, few, more, most, other, some, such, no, nor, not, only, own, same, so, than, too, very, just, also, well, please, experience, work, team). Descriptions shorter than 10 words are assumed to be English. |

### Logic

```
is_remote = doc.is_remote == true
is_germany = location matches any Germany keyword
english = description has > 8% English stop words (or < 10 words total)

applicable = (is_remote OR is_germany) AND english
```
