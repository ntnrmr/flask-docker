# Flask SQLalchemy app

Example Flask application which stores data in PostgreSQL database

## Development setup

Install dependencies and develop locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Run application locally with docker-compose

```bash
pip install docker-compose
docker-compose up --build
```

Run pre commit hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Run tests

```bash
source .venv/bin/activate
pytest test_app.py
```
