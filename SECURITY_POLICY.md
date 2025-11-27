# Security Policy

## Supported Versions
This repository is provided for educational use. Security fixes are applied to `main` on a best-effort basis. Always pin to a tagged release for reproducibility.

## Reporting a Vulnerability
- Email `security@example.invalid` with details, reproduction steps, and potential impact.
- Do **not** open public issues for security vulnerabilities until a fix is available.
- Encrypt sensitive reports if preferred; request a PGP key via email.

## Secure Development Practices
- No production secrets are stored in the repo.
- Input validation is enforced via Pydantic schemas and server-side FAIR parameter checks.
- Dependencies should be kept updated; run `pip list --outdated` periodically and patch CVEs promptly.
- Restrict CORS origins in production and avoid exposing management endpoints publicly.
- Validate and scrub uploaded data before using it in reports; PDF generation writes to a temporary file only.
