# SAFE-NET Architecture

SAFE-NET is a 4-layer stack:
1. Flutter mobile app (SOS, check-ins, covert trigger)
2. Meshtastic LoRa mesh for disconnected zones
3. FastAPI + PostGIS + Redis/Celery backend
4. Next.js dashboard with live mapping and admin controls
