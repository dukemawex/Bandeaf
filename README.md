# SAFE-NET (Bandeaf)

SAFE-NET is an open-source emergency safety and anti-kidnapping alert platform designed for rural and forested high-risk regions.

## Stack

- **Mobile:** Flutter (Android/iOS)
- **Offline Mesh:** Meshtastic LoRa + Raspberry Pi gateway
- **Backend:** FastAPI + PostgreSQL/PostGIS + Redis + Celery
- **Dashboard:** Next.js 14 + Leaflet + Recharts
- **CI/CD:** GitHub Actions
- **License:** AGPL v3

## Repository Layout

```text
safe-net/
├── backend/
├── mobile/
├── dashboard/
├── mesh-gateway/
├── hardware/
├── docs/
├── docker-compose.yml
├── docker-compose.dev.yml
└── .github/workflows/
```

## Core Backend Endpoints

- `POST /api/v1/alert/sos`
- `POST /api/v1/alert/checkin`
- `POST /api/v1/alert/mesh-gateway`
- `POST /api/v1/alert/sms-inbound`
- `GET /api/v1/zones/danger`
- `POST /api/v1/user/route`
- `GET /api/v1/user/route`
- `GET /api/v1/stream/alerts`

## Deployment Options

### Option A: Minimal (<$10/mo)
- Single VPS running Docker Compose (PostGIS, Redis, API, Celery, Nginx)
- Dashboard on Vercel free tier
- Mesh gateway forwarding over LTE modem or Starlink

### Option B: Community-Hosted (Offline-first)
- Raspberry Pi 4 local server with Starlink backhaul
- Local-first operations with sync when internet returns

### Option C: Cloud Scale
- Backend on Render/Railway
- PostGIS on Supabase
- Dashboard on Vercel

## Quick Start

See [docs/QUICKSTART.md](docs/QUICKSTART.md).

## Security Baseline

- JWT authentication for protected routes
- Bcrypt password hashing
- HMAC verification for mesh/SMS inbound
- Rate limiting via `slowapi`
- Log redaction for sensitive fields
