# MDIA - Maintenance Document Intelligence Assistant

A full-stack AI-powered application for modernizing MSC-style engineering and maintenance workflows. MDIA enables document ingestion, structured data extraction using LLMs, legacy Excel modernization, anomaly detection, status tracking, and automated engineering document generation.

## Features

- **Document Upload & Processing**: Accept PDFs, Excel, CSV, and log files
- **AI-Powered Extraction**: Uses free Hugging Face LLMs (Mistral-7B) for structured data extraction
- **Legacy Excel Conversion**: Auto-map old-format MSC maintenance spreadsheets to normalized schema
- **Anomaly Detection**: Automatically flag data quality issues (date inconsistencies, missing fields, extreme values)
- **Maintenance Status Board**: Track maintenance items through open, in-progress, awaiting-parts, complete stages
- **CAP Generation**: Generate Corrective Action Plans as Markdown documents
- **Professional Dashboard**: WCAG AA accessible React UI with clean maritime/engineering aesthetic

## Architecture

```
[React Frontend]        [FastAPI Backend]         [PostgreSQL]
     |                        |                        |
     |-- Upload ------------>|-- Store Metadata ----->|
     |-- View Documents ---->|-- Extract Text ------->|
     |-- Status Updates ---->|-- LLM Extraction ----->|
     |-- Generate CAP ------>|-- Anomaly Detection -->|
     |                        |-- Store Records ----->|
```

## Tech Stack

**Backend:**
- Python 3.11, FastAPI, SQLAlchemy
- pdfplumber (PDF extraction), pandas (Excel/CSV)
- Hugging Face Inference API

**Frontend:**
- React 18, TypeScript, Vite
- Custom CSS design system (no external dependencies)

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL 15

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) Free Hugging Face API token for LLM features

### 1. Clone and Configure

```bash
cd CACI-Maintenance-Document-Intelligence-Assistant

# Copy environment template
cp .env.example .env

# (Optional) Add your Hugging Face token to .env
# Get one free at: https://huggingface.co/settings/tokens
```

### 2. Start Services

```bash
docker-compose up --build
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:3000
- **PostgreSQL**: localhost:5432

### 3. Access the Application

Open http://localhost:3000 in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /upload | Upload a document |
| GET | /documents | List all documents |
| GET | /documents/{id} | Get document details |
| POST | /ingest/{id} | Process a document |
| POST | /legacy/convert | Convert legacy Excel file |
| GET | /records | List extracted records |
| PATCH | /record/{id}/status | Update record status |
| GET | /status/overview | Get status statistics |
| GET | /report/summary?document_id= | Generate summary report |
| GET | /report/cap?document_id= | Generate Corrective Action Plan |

## Project Structure

```
├── backend/
│   ├── api/routes/          # FastAPI route handlers
│   ├── db/                   # Database configuration
│   ├── ingestion/            # Document extraction modules
│   ├── llm/                  # LLM client and prompts
│   ├── models/               # SQLAlchemy models & Pydantic schemas
│   ├── reports/              # Report generation
│   ├── services/             # Business logic
│   └── tests/                # Pytest tests
├── frontend/
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # Reusable React components
│   │   └── pages/            # Page components
├── db/
│   └── schema.sql            # PostgreSQL schema
├── samples/                  # Sample test documents
├── docker-compose.yml
└── README.md
```

## Development

### Running Backend Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
cd backend
pytest tests/ -v
```

## LLM Configuration

MDIA uses the free Hugging Face Inference API by default. Without a token, the system falls back to regex-based extraction.

To enable full LLM features:
1. Create a free account at [Hugging Face](https://huggingface.co)
2. Generate an API token at https://huggingface.co/settings/tokens
3. Add it to your `.env` file: `HF_TOKEN=your_token_here`

## Sample Data

The `samples/` directory contains test files:
- `maintenance_records.csv` - Clean CSV format
- `sample_maintenance_log.txt` - Legacy MSC-style log

## Accessibility

The UI is designed to meet WCAG AA standards:
- High contrast color ratios (minimum 4.5:1)
- Semantic HTML structure
- Full keyboard navigation
- Visible focus indicators
- Screen reader compatible

## Secure Deployment Considerations

This demo runs in a local development environment. For deployment in a **secure government or enterprise environment** (e.g., MSC/Navy networks, FedRAMP, IL4/IL5), the following measures would need to be implemented:

### Network Security

| Measure | Implementation |
|---------|----------------|
| **Network Isolation** | Deploy in a private VPC/VLAN with no direct internet access |
| **Reverse Proxy** | Use nginx/HAProxy with TLS termination in front of all services |
| **TLS Encryption** | Enforce TLS 1.3 for all traffic; use DoD-approved certificates |
| **Firewall Rules** | Whitelist-only ingress; restrict egress to approved endpoints |
| **Web Application Firewall** | Deploy WAF (e.g., ModSecurity) for OWASP protection |

### Authentication & Authorization

| Measure | Implementation |
|---------|----------------|
| **CAC/PIV Integration** | Integrate with DoD PKI for smart card authentication |
| **SSO/SAML** | Connect to enterprise IdP (ADFS, Okta, Keycloak) |
| **RBAC** | Implement role-based access (Admin, Engineer, Viewer) |
| **Session Management** | Short-lived JWTs, secure cookies, automatic timeout |
| **Audit Logging** | Log all authentication events and data access |

### Data Protection

| Measure | Implementation |
|---------|----------------|
| **Encryption at Rest** | Use PostgreSQL TDE or encrypted storage volumes |
| **Encryption in Transit** | TLS for all service-to-service communication |
| **Data Classification** | Tag records with CUI/FOUO labels as appropriate |
| **Backup Encryption** | Encrypt all backups with separate key management |
| **Data Retention** | Implement automated retention policies per NARA guidelines |

### LLM/AI Security for Air-Gapped Environments

For classified or air-gapped networks where external API calls are prohibited:

```
Option 1: Local Model Deployment
- Deploy Mistral-7B or similar on local GPU infrastructure
- Use vLLM or Text Generation Inference for serving
- No external network calls required

Option 2: Approved Cloud AI Services
- Use FedRAMP-authorized AI services (Azure Government, AWS GovCloud)
- Ensure data residency requirements are met
- Implement API gateway with egress filtering
```

### Container Security

| Measure | Implementation |
|---------|----------------|
| **Image Scanning** | Scan all images with Trivy/Clair before deployment |
| **Base Images** | Use Iron Bank / DoD-hardened base images |
| **Read-Only Containers** | Run containers with read-only root filesystem |
| **Non-Root Execution** | All containers run as non-root users |
| **Secrets Management** | Use HashiCorp Vault or K8s secrets (encrypted) |

### Compliance Frameworks

| Framework | Key Requirements |
|-----------|------------------|
| **NIST 800-53** | Access control, audit, system integrity controls |
| **FedRAMP** | Moderate/High baseline for cloud deployments |
| **STIG** | Apply OS, database, and container STIGs |
| **RMF** | Complete ATO package with SSP, SAR, POA&M |

### Deployment Architecture (Secure)

```
                    ┌─────────────────────────────────────────────┐
                    │           Secure Network Boundary           │
                    │  ┌─────────────────────────────────────┐   │
    CAC/PIV Auth    │  │         Kubernetes Cluster          │   │
         │          │  │  ┌─────────┐  ┌─────────┐           │   │
         ▼          │  │  │ Frontend│  │ Backend │──┐        │   │
    ┌────────┐      │  │  │  (TLS)  │  │  (TLS)  │  │        │   │
    │  WAF/  │──────┼──┼─▶│         │  │         │  ▼        │   │
    │ Proxy  │      │  │  └─────────┘  └─────────┘ ┌──────┐  │   │
    └────────┘      │  │                           │ PG   │  │   │
                    │  │  ┌─────────────┐          │(Enc) │  │   │
                    │  │  │ Local LLM   │◀─────────┴──────┘  │   │
                    │  │  │ (GPU Node)  │                    │   │
                    │  │  └─────────────┘                    │   │
                    │  └─────────────────────────────────────┘   │
                    │              Audit Logs ──▶ SIEM           │
                    └─────────────────────────────────────────────┘
```

### Key Modifications for Production

1. **Remove development settings**: Disable `--reload`, debug modes, CORS wildcards
2. **Implement health checks**: Add liveness/readiness probes for orchestration
3. **Add rate limiting**: Protect API endpoints from abuse
4. **Enable HTTPS only**: Redirect all HTTP to HTTPS, set HSTS headers
5. **Harden PostgreSQL**: Disable default accounts, enable connection encryption.

## License

Demo project for CACI MSC N7 Modernization Program
