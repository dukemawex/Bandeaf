# SAFE-NET Quickstart (Under 30 Minutes)

1. Copy `.env.example` to `.env` and update secrets.
2. `docker compose up --build -d`
3. Open API at `http://localhost:8000/api/v1/health`
4. Run backend tests: `cd backend && pytest -q`
