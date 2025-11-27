.PHONY: install lint format test run serve precommit

install:
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

lint:
ruff check .
black --check .
isort --check-only .
mypy .

format:
ruff check --fix .
black .
isort .

precommit:
pre-commit run --all-files

test:
pytest

run:
uvicorn backend.main:app --reload

serve:
uvicorn backend.main:app --host 0.0.0.0 --port 8000
