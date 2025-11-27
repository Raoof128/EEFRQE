# API Reference

All endpoints are served by FastAPI. Interactive documentation is available at `/docs`.

## Health
- `GET /health` → `{ "status": "ok" }`

## Essential Eight
- **Endpoint**: `POST /e8/score`
- **Description**: Calculate Essential Eight maturity and regulatory signals.
- **Payload**:
```json
{
  "organisation": "Synthetic Org",
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
}
```
- **Response (excerpt)**:
```json
{
  "organisation": "Synthetic Org",
  "overall_level": 1.63,
  "control_results": [
    {"control": "application_control", "level": 2, "heat": "moderate", "risk_implication": "..."}
  ],
  "regulatory_signals": [
    {"regulation": "Privacy Act (OAIC)", "impact": "...", "recommendation": "..."}
  ]
}
```

## FAIR Calculation
- **Endpoint**: `POST /fair/calc`
- **Description**: Run FAIR Monte Carlo simulation using triangular distributions `(min, mode, max)`.
- **Payload**:
```json
{
  "threat_event_frequency": [2,6,12],
  "vulnerability": [0.3,0.5,0.8],
  "primary_loss": [200000,400000,800000],
  "secondary_loss": [50000,150000,300000],
  "secondary_event_frequency": [0.5,1,3]
}
```
- **Response (excerpt)**:
```json
{
  "loss_event_frequency": 3.1,
  "loss_magnitude": {"primary": 400000, "secondary": 150000, "total": 550000},
  "monte_carlo": {"mean": 3100000, "p95": 5800000, "worst_case": 8800000}
}
```

## Scenario Execution
- **Endpoint**: `POST /scenario/run`
- **Description**: Apply Essential Eight controls to predefined scenarios (ransomware, bec, data_breach).
- **Payload**: Same control list as `/e8/score` but as an array with `control` and `level`.
- **Response (excerpt)**:
```json
{
  "scenario": "ransomware",
  "base_stats": {
    "loss_event_frequency": 4.2,
    "secondary_event_frequency": 1.2,
    "primary_loss": 420000,
    "secondary_loss": 180000
  },
  "monte_carlo": {"mean": 3400000, "p95": 6200000, "worst_case": 9100000}
}
```

## Reporting
- **Endpoint**: `POST /report/pdf`
- **Description**: Accepts E8 and FAIR outputs plus recommendations, returns a PDF report.
- **Notes**: The endpoint writes to a temporary file before returning; ensure disk access is permitted in your environment.
