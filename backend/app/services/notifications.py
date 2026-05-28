from __future__ import annotations

import logging
from datetime import datetime, timezone

import africastalking
import firebase_admin
from firebase_admin import credentials, initialize_app, messaging
from twilio.rest import Client

from app.core.config import settings
from app.services.store import STORE

logger = logging.getLogger("safenet.notifications")
_firebase_ready = False


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
    send_success = False
    error: str | None = None
    if settings.AFRICASTALKING_API_KEY and settings.AFRICASTALKING_USERNAME:
        try:
            africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
            africastalking.SMS.send(message, [phone], sender_id=settings.SMS_SENDER_ID)
            send_success = True
        except Exception as exc:
            error = f"Africa's Talking failed: {exc.__class__.__name__}"
            logger.warning(error)

    if not send_success and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(to=phone, from_=settings.SMS_SENDER_ID, body=message)
            send_success = True
        except Exception as exc:
            error = f"Twilio failed: {exc.__class__.__name__}"
            logger.warning(error)

    if alert_id:
        _mark_notification(alert_id, "sms", phone, "sent" if send_success else "failed", error)
    return send_success


def send_push(device_token: str, title: str, body: str, alert_id: str | None = None) -> bool:
    global _firebase_ready
    success = False
    error: str | None = None
    if settings.FCM_CREDENTIALS_FILE:
        try:
            if not _firebase_ready and not firebase_admin._apps:
                initialize_app(credentials.Certificate(settings.FCM_CREDENTIALS_FILE))
                _firebase_ready = True
            message = messaging.Message(notification=messaging.Notification(title=title, body=body), token=device_token)
            messaging.send(message)
            success = True
        except Exception as exc:
            error = f"FCM failed: {exc.__class__.__name__}"
            logger.warning(error)

    if alert_id:
        _mark_notification(alert_id, "fcm", device_token, "sent" if success else "failed", error)
    return success


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
