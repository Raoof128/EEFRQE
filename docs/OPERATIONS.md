# Operations & Deployment Runbook

## Local development
- Install dependencies: `pip install -r requirements.txt`
- Start API: `uvicorn backend.main:app --reload`
- Run tests/lint: `make lint test`

## Containerisation
- Build: `docker build -t e8-fair-engine .`
- Run: `docker run -p 8000:8000 --env-file .env.example e8-fair-engine`
- Override config via `E8_FAIR_*` environment variables.

## Logging
- Configurable via `E8_FAIR_LOG_LEVEL` (DEBUG/INFO/WARNING/ERROR/CRITICAL).
- Structured format: `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`.
- Recommendation: ship stdout to central logging (CloudWatch, ELK, etc.).

## Monitoring & Health
- `/health` endpoint returns `{ "status": "ok" }` for liveness.
- Use HTTP probes in orchestrators (Kubernetes, ECS) with fast intervals.

## Security
- Restrict `E8_FAIR_CORS_ORIGINS` to trusted hosts in production.
- Keep `.env` files out of source control; use secrets managers.
- PDF outputs write to `E8_FAIR_PDF_OUTPUT_DIR`; set to writeable, isolated path.

## Backups & Reports
- Generated PDFs land under the configured output directory; consider log shipping or archival with retention policies.
- The engine only handles synthetic data by default; treat uploaded data per organisational policies.

## Deployment targets
- **Docker**: run container behind API gateway/reverse proxy.
- **Serverless**: package FastAPI with an ASGI adapter (e.g., AWS Lambda + Lambda Web Adapter).
- **On-prem**: run via systemd service calling `uvicorn backend.main:app` with virtualenv.

## Disaster recovery
- Rebuild containers from source; seed environment variables from config management.
- Validate Monte Carlo iteration settings remain >= 1000 to avoid degraded statistical output.
