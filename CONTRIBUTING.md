# Contributing

Thank you for considering contributing! To maintain quality and safety:
1. Fork the repository and create feature branches.
2. Install and run `pre-commit` hooks (`make precommit`) before submitting PRs.
3. Run `make lint test` to execute ruff, black, isort, mypy, and pytest.
4. Add tests and documentation for new features, including API examples where relevant.
5. Use descriptive commit messages and follow semantic PR titles.

## Development Environment
- Python 3.11+
- Install dependencies with `pip install -r requirements.txt`.
- Start the API locally via `uvicorn backend.main:app --reload` or `make run`.
- Optionally run inside Docker: `docker build -t e8-fair-engine . && docker run -p 8000:8000 e8-fair-engine`.

## Reporting Issues
Please include reproduction steps, expected behaviour, and environment details. For security issues, use the contact in `SECURITY_POLICY.md` and do not open public issues.
