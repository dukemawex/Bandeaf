# Mesh Gateway Deployment

1. Install Python 3.11+, pip, and `meshtastic` CLI on Raspberry Pi/Orange Pi.
2. Copy `gateway.py` and `safenet-gateway.service` to `/opt/safe-net/mesh-gateway/`.
3. Set `MESH_GATEWAY_HMAC_SECRET`, `BACKEND_URL`, and optional modem connectivity variables.
4. Enable service:
   - `sudo cp safenet-gateway.service /etc/systemd/system/`
   - `sudo systemctl daemon-reload`
   - `sudo systemctl enable --now safenet-gateway`
5. Verify logs with `journalctl -u safenet-gateway -f`.
