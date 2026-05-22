# Use Python 3.14 slim image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN pip install --no-cache-dir \
    uv \
    requests \
    pymongo \
    python-dotenv \
    weasyprint>=68.1 \
    markdown>=3.10.2 \
    typst>=0.14.9 \
    fastapi \
    uvicorn[standard] \
    langchain>=0.3.0 \
    langchain-anthropic>=0.3.0 \
    langchain-openai>=0.3.0 \
    langchain-community \
    langchain-text-splitters \
    langchain-huggingface \
    chromadb \
    pypdf \
    sentence-transformers

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "app.main"]
