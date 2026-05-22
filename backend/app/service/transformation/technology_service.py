import json
from langchain_core.prompts import ChatPromptTemplate
from app.core.data_unified_repository import unified_jobs_collection
from app.service.llm_config import get_llm

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """You are a technical recruiter extracting technologies from a job offer.

From the job title and description, extract all mentioned technologies, frameworks, tools, platforms, and programming languages.

Use this keyword list as your reference (but do not limit yourself to it — infer technologies even if phrased differently):

**Languages:** Java, Python, JavaScript, TypeScript, Kotlin, Golang, Rust, C++, C#, PHP, Ruby, Scala, Swift, Dart, Perl

**Frameworks & Libraries:** Spring Boot, Spring Cloud, Spring Framework, React, Angular, Vue.js, Next.js, Nuxt, Svelte, EmberJS, Node.js, Express, Django, Flask, FastAPI, .NET, ASP.NET, ASP.NET Core, Hibernate, JPA, MyBatis, Lombok, TensorFlow, PyTorch, Keras, scikit-learn, LangChain, LangGraph, LlamaIndex, Prisma, TypeORM, Mongoose, SQLAlchemy, Pandas, NumPy, Matplotlib, RxJS, Redux, NgRx, Zustand

**Cloud & Infrastructure:** Docker, Kubernetes, Terraform, Ansible, Jenkins, AWS, Amazon Web Services, Azure, Google Cloud, GCP, Lambda, ECS, EC2, S3, CloudFront, DynamoDB, RDS, CloudFormation, Event Hub, Cosmos DB, Azure Functions, Helm, Istio, Prometheus, Grafana, Datadog

**Databases & Message Queues:** PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, SQLite, MongoDB, Elasticsearch, Redis, Cassandra, Neo4j, Couchbase, Kafka, RabbitMQ, ActiveMQ, SQS, SNS

**AI/ML:** RAG, Retrieval-Augmented Generation, LLM, Large Language Model, OpenAI, Claude, Gemini, Prompt Engineering, Multi-Agent, Agentic, Machine Learning, Artificial Intelligence, Computer Vision, NLP, Natural Language Processing

**DevOps & Tools:** Git, GitHub, GitLab, Bitbucket, GitHub Actions, CI/CD, CircleCI, Travis CI, GitLab CI, Docker Compose, Devcontainer, Webpack, Vite, ESLint, Prettier, Nginx, Apache, Tomcat, JBoss, WildFly, Linux, Unix

**Testing:** JUnit, Mockito, Cypress, Selenium, Pytest, Jasmine, Karma, TDD, BDD

**Frontend:** Effect, React , Tailwind, HTML, CSS, SCSS, Tailwind CSS, Bootstrap, Material UI, Chakra UI, React Native, Flutter, Android, iOS

**Other:** SAP, Salesforce, ServiceNow, Appsmith, Nextcloud, Microservices, Event-Driven, Agile, Scrum, Kanban, Data Science, Data Engineering, GraphQL, gRPC

Return a sorted JSON array of unique technology names using the canonical casing from the keyword list above.
If no technologies are found, return an empty array [].

Example: ["AWS", "Angular", "Docker", "Java", "Spring Boot"]"""),
    ("human", "Title: {title}\n\nDescription:\n{description}"),
])


def process_technologies(batch_size: int = 50) -> tuple[int, int]:
    llm = get_llm()
    chain = PROMPT_TEMPLATE | llm

    query = {
        "applicable": True,
        "$or": [
            {"technologies": {"$exists": False}},
            {"technologies": {"$eq": []}},
            {"technologies": None},
        ],
    }
    total = unified_jobs_collection.count_documents(query)
    processed = 0
    errors = 0

    cursor = unified_jobs_collection.find(query).limit(batch_size).batch_size(batch_size)

    for doc in cursor:
        try:
            title = doc.get("title") or doc.get("job_title") or ""
            description = (doc.get("description") or doc.get("description_text") or "")[:3000]

            response = chain.invoke({
                "title": title,
                "description": description,
            })

            content = response.content.strip()
            if content.startswith("```"):
                content = content.strip("`").strip()
                if content.startswith("json"):
                    content = content[4:].strip()

            technologies = json.loads(content)
            if not isinstance(technologies, list):
                technologies = []

            unified_jobs_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"technologies": technologies}}
            )
            processed += 1

        except Exception as e:
            print(f"  [ERROR] technologies: {doc.get('title', '?')[:50]} → {e}")
            unified_jobs_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"technologies": []}}
            )
            errors += 1

    print(f"  technologies: {processed} ok, {errors} errors (total pending: {total})")
    return processed, errors
