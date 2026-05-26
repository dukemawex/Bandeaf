from __future__ import annotations

from datetime import datetime, timedelta, timezone

from celery import shared_task

from app.services.notifications import notify_community_responders, notify_emergency_contacts
from app.services.store import STORE


@shared_task(name="safenet.notify_emergency_contacts")
def task_notify_emergency_contacts(alert_id: str) -> str:
    alert = STORE.alerts.get(alert_id)
    if alert:
        notify_emergency_contacts(alert)
    return alert_id


@shared_task(name="safenet.notify_community_responders")
def task_notify_community_responders(alert_id: str) -> str:
    alert = STORE.alerts.get(alert_id)
    if alert:
        notify_community_responders(alert)
    return alert_id


@shared_task(name="safenet.missed_checkin_monitor")
def missed_checkin_monitor() -> int:
    now = datetime.now(tz=timezone.utc)
    escalations = 0
    for user in STORE.users.values():
        last_seen = user.get("last_seen")
        interval = timedelta(seconds=int(user.get("checkin_interval") or 3600) + 600)
        if last_seen is None or last_seen + interval < now:
            alert = STORE.create_alert(
                user_id=user["id"],
                alert_type="MISSED_CHECKIN",
                source="app",
                location=None,
                accuracy=None,
                battery=None,
                message="Missed scheduled check-in",
            )
            notify_emergency_contacts(alert)
            notify_community_responders(alert)
            escalations += 1
    return escalations
