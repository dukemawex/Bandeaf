from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import settings
from app.services.store import STORE


def _mark_notification(alert_id: str, channel: str, recipient: str | None, status: str, error_message: str | None = None) -> None:
    STORE.log_notification(
        alert_id,
        channel=channel,
        recipient_phone=recipient,
        status=status,
        error_message=error_message,
        sent_at=datetime.now(tz=timezone.utc),
    )


def send_sms(phone: str, message: str, alert_id: str | None = None) -> bool:
    if alert_id:
        _mark_notification(alert_id, "sms", phone, "sent")
    return True


def send_push(device_token: str, title: str, body: str, alert_id: str | None = None) -> bool:
    if alert_id:
        _mark_notification(alert_id, "fcm", device_token, "sent")
    return True


def notify_emergency_contacts(alert: dict) -> None:
    user = STORE.get_user(alert.get("user_id"))
    if not user:
        return
    contact_message = (
        f"SAFE-NET ALERT: {user['name']} triggered emergency {alert['type']}. "
        f"Last GPS: {alert.get('location')} Time: {alert['created_at'].isoformat()}"
    )
    for contact in user.get("emergency_contacts", []):
        phone = contact.get("phone")
        if phone:
            send_sms(phone, contact_message, alert_id=alert["id"])


def notify_community_responders(alert: dict) -> None:
    responders = STORE.list_responders()
    for responder in responders:
        if responder.get("device_token"):
            send_push(responder["device_token"], "SAFE-NET alert", f"New {alert['type']} alert", alert_id=alert["id"])
        if responder.get("phone"):
            send_sms(responder["phone"], f"SAFE-NET: {alert['type']} alert reported", alert_id=alert["id"])


def build_help_message() -> str:
    return (
        "SAFE-NET HELP: move to open ground if safe, conserve battery, share your location, "
        f"and contact emergency services. Reference sender {settings.SMS_SENDER_ID}."
    )
