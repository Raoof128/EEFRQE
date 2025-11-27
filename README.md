# Essential Eight + FAIR Cyber Risk Quantification Engine

Enterprise-grade platform that combines the Australian Cyber Security Centre (ACSC) Essential Eight maturity model with FAIR (Factor Analysis of Information Risk) quantitative risk analysis. The stack uses FastAPI for the backend and a lightweight HTML/Chart.js dashboard for quick visualisation. All example values are synthetic and provided for educational use.

## Features
- **Essential Eight assessment**: Rule-based maturity scoring (levels 0–3) with control-level heatmaps and remediation tips.
- **FAIR quantification**: Loss Event Frequency (LEF), Loss Magnitude (LM), and Monte Carlo simulation (10k iterations by default).
- **Scenario builder**: Ransomware, Business Email Compromise, and Data Breach scenarios with Essential Eight-informed parameter adjustments.
- **Australian regulatory lens**: Signals for Privacy Act (OAIC), SOCI Act, and APRA CPS 234 where relevant.
- **Reporting**: Executive-ready PDF export summarising maturity, risk simulations, and recommendations.
- **API-first**: FastAPI endpoints for assessments, FAIR calculations, scenario execution, PDF export, and health checks.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
Visit the interactive docs at `http://127.0.0.1:8000/docs`.

### Docker
```bash
docker build -t e8-fair-engine .
docker run -p 8000:8000 --env-file .env.example e8-fair-engine
```

### Make targets
- `make lint` – run ruff, black, isort, and mypy
- `make test` – execute pytest suite
- `make run` – start local dev server with reload
- `make precommit` – run the configured pre-commit hooks

### Configuration
Runtime is configurable via environment variables (prefixed with `E8_FAIR_`). Defaults are safe for local use:

| Variable | Description | Default |
| --- | --- | --- |
| `E8_FAIR_CORS_ORIGINS` | JSON array of allowed origins for CORS. | `["http://127.0.0.1:3000","http://localhost:3000"]` |
| `E8_FAIR_MONTE_CARLO_ITERATIONS` | Monte Carlo iterations (min 1000). | `10000` |
| `E8_FAIR_PDF_OUTPUT_DIR` | Directory to write generated reports. | `reports` |
| `E8_FAIR_LOG_LEVEL` | Log level for API output. | `INFO` |

### Running tests & linting
```bash
make lint
make test
```

## API Overview
- `POST /e8/score` – Calculate Essential Eight maturity with regulatory signals.
- `POST /fair/calc` – Run FAIR Monte Carlo.
- `POST /scenario/run` – Execute a risk scenario using E8-informed adjustments.
- `POST /report/pdf` – Generate an executive PDF report.
- `GET /health` – Service liveness.

Detailed request/response schemas are documented in [docs/API.md](docs/API.md) and surfaced in the OpenAPI UI.

## Repository Structure
```
backend/
  main.py
  api/
    e8.py
    fair.py
    scenario.py
    reports.py
  engines/
    e8_score.py
    fair_calc.py
    monte_carlo.py
    regulation_mapping.py
    risk_mapper.py
    scenario_engine.py
  utils/
    pdf_export.py
  schemas.py
frontend/
  index.html
  dashboard.js
  styles.css
docs/
  ARCHITECTURE.md
  METHODOLOGY.md
  API.md
  OPERATIONS.md
requirements.txt
pyproject.toml
README.md
LICENSE
CODE_OF_CONDUCT.md
CONTRIBUTING.md
SECURITY_POLICY.md
Dockerfile
.env.example
.pre-commit-config.yaml
.editorconfig
```

## Developer Tooling
- **Pre-commit**: install via `pip install pre-commit` and run `make precommit`.
- **Static analysis**: ruff, black, isort, and mypy are configured in `pyproject.toml`.
- **Container**: packaged with a slim Python 3.11 base (`Dockerfile`).

## Usage Examples
### Essential Eight
```bash
curl -X POST http://127.0.0.1:8000/e8/score \
  -H "Content-Type: application/json" \
  -d '{
    "organisation": "Synthetic Bank",
    "industry": "finance",
    "assessments": {
      "application_control": {"level": 2},
      "patch_applications": {"level": 2},
      "configure_ms_office_macros": {"level": 1},
      "user_application_hardening": {"level": 2},
      "restrict_admin_privileges": {"level": 1},
      "patch_operating_systems": {"level": 2},
      "multi_factor_authentication": {"level": 1},
      "regular_backups": {"level": 2}
    }
  }'
```

### FAIR Calculation
```bash
curl -X POST http://127.0.0.1:8000/fair/calc \
  -H "Content-Type: application/json" \
  -d '{
    "threat_event_frequency": [2,6,12],
    "vulnerability": [0.3,0.5,0.8],
    "primary_loss": [200000,400000,800000],
    "secondary_loss": [50000,150000,300000],
    "secondary_event_frequency": [0.5,1,3]
  }'
```

### Scenario Execution
```bash
curl -X POST http://127.0.0.1:8000/scenario/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_key": "ransomware",
    "controls": [
      {"control": "application_control", "level": 2},
      {"control": "patch_applications", "level": 2},
      {"control": "configure_ms_office_macros", "level": 1},
      {"control": "user_application_hardening", "level": 2},
      {"control": "restrict_admin_privileges", "level": 1},
      {"control": "patch_operating_systems", "level": 2},
      {"control": "multi_factor_authentication", "level": 1},
      {"control": "regular_backups", "level": 2}
    ]
  }'
```

## Safety & Disclaimers
- All figures are synthetic estimates and **not legal advice**.
- Use the platform as decision support, not as definitive regulatory guidance.
- Restrict CORS origins to trusted domains before production deployment.

## License
Released under the MIT License. See [LICENSE](LICENSE).
