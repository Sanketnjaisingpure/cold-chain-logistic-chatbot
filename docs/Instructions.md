# Ingesting data

- Download the dataset from 'data\source\data.txt'
# Python Project Setup with Docker and GCP Cloud SQL

## 1. Objective

This document provides a reusable guide for setting up a Python project with:

- Google Cloud Platform (GCP)
- Cloud SQL (PostgreSQL)
- Docker and Docker Compose
- Cloud SQL Auth Proxy
- Python database connectivity using SQLAlchemy

The goal is to establish a repeatable development environment that can be reused across projects.

## 2. Prerequisites

Install the following tools:

| Tool | Purpose |
|---|---|
| Python | Application development |
| Docker Desktop | Containerization |
| Google Cloud CLI | GCP authentication and resource management |
| PostgreSQL client | Database access and verification |
| Git | Version control |

## 3. GCP Initial Setup

For a new project:

1. Create a GCP project.
2. Enable the Cloud SQL Admin API.
3. Create a Cloud SQL PostgreSQL instance.
4. Create a PostgreSQL database and application user.
5. Configure IAM permissions using `roles/cloudsql.client`.
6. Note the Cloud SQL instance connection name.

## 4. Local GCP Authentication

Install Google Cloud CLI and authenticate:

```powershell
gcloud auth login
```

Configure the project:

```powershell
gcloud config set project YOUR_PROJECT_ID
```

Configure Application Default Credentials:

```powershell
gcloud auth application-default login
```

Set the quota project:

```powershell
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

Verify the ADC credentials file:

```powershell
Test-Path "$env:APPDATA\gcloud\application_default_credentials.json"
```

Expected output: `True`.

## 5. Python Project Structure

Use a clean, modular structure:

```text
my-python-project/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│
├── src/
│
├── docs/
│
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── app.py
```

## 6. Docker Configuration

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

Create `docker-compose.yml` with two services:

1. Application container
2. Cloud SQL Auth Proxy container

The proxy authenticates using ADC credentials mounted from the host machine.

The application connects to the proxy using:

```text
Host: cloud-sql-proxy
Port: 5432
```

Use the Cloud SQL instance connection name in the proxy configuration:

```text
PROJECT_ID:REGION:INSTANCE_NAME
```

## 7. Database Configuration

Store database settings in `.env`:

```properties
DB_HOST=cloud-sql-proxy
DB_PORT=5432
DB_NAME=YOUR_DATABASE
DB_USER=YOUR_DATABASE_USER
DB_PASSWORD=YOUR_DATABASE_PASSWORD
```

Connect using SQLAlchemy:

```python
from sqlalchemy import URL, create_engine
import os

connection_url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 5432)),
    database=os.getenv("DB_NAME")
)

engine = create_engine(connection_url)
```

## 8. Build and Run

Build the application image:

```powershell
docker compose build
```

Start the Cloud SQL Auth Proxy:

```powershell
docker compose up -d cloud-sql-proxy
```

Check proxy logs:

```powershell
docker compose logs -f cloud-sql-proxy
```

Start the application:

```powershell
docker compose up app
```

Service names and commands should match your actual Compose configuration.

## 9. Shutdown and Restart

Stop and remove containers:

```powershell
docker compose down
```

Restart the proxy:

```powershell
docker compose up -d cloud-sql-proxy
```

Stopping Docker containers does not delete data stored in Cloud SQL.

Avoid destructive database operations unless explicitly intended.

## 10. Security Guidelines

- Never commit `.env` or credential files to Git.
- Use `.gitignore` for secrets and local environments.
- Never expose PostgreSQL publicly just to enable application connectivity.
- Use Cloud SQL Auth Proxy for secure connectivity.
- Grant only the IAM permissions required.
- Prefer dedicated database users instead of administrator accounts.
- Use Secret Manager or an equivalent secrets-management solution for production.

## 11. Reusable Workflow

For future projects, follow this sequence:

1. Create the GCP project and Cloud SQL instance.
2. Configure IAM and authentication.
3. Create the Python project structure.
4. Configure dependencies and environment variables.
5. Create the Dockerfile.
6. Configure Docker Compose and Cloud SQL Auth Proxy.
7. Build the application image.
8. Start the proxy.
9. Run and verify the application.
10. Shut down unused resources and review cloud costs.

---

**Document scope:** This guide covers the initial infrastructure, authentication, containerization, and database connectivity setup. Application-specific architecture, data ingestion, APIs, and deployment are documented separately as the project evolves.