import csv
import hashlib
import io
import secrets
import uuid
from datetime import timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from .models import Guest, InviteToken


def import_guests_from_csv(event, file_content: str) -> tuple[int, list[dict[str, Any]]]:
    """Import guests from CSV content with streaming parsing, validation, and batch persistence."""
    reader = csv.DictReader(io.StringIO(file_content))
    created_count = 0
    errors = []
    guests_to_create = []
    tokens_to_create = []

    with transaction.atomic():
        for row_num, row in enumerate(reader, start=2):
            name = (row.get("name") or row.get("Name") or "").strip()
            email = (row.get("email") or row.get("Email") or "").strip()
            plus_ones_str = (row.get("plus_ones") or row.get("Plus Ones") or "0").strip()
            dietary = (row.get("dietary") or row.get("Dietary") or "").strip()

            if not name:
                errors.append({"row": row_num, "error": "Name is required"})
                continue

            try:
                plus_ones = max(0, int(plus_ones_str))
            except ValueError:
                errors.append(
                    {
                        "row": row_num,
                        "error": f"Invalid plus_ones count '{plus_ones_str}'",
                    }
                )
                continue

            guest_id = uuid.uuid4()
            guest = Guest(
                id=guest_id,
                event=event,
                name=name,
                email=email,
                plus_ones=plus_ones,
                dietary_requirements=dietary,
            )
            guests_to_create.append(guest)

            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
            expires_at = timezone.now() + timedelta(days=30)
            tokens_to_create.append(
                InviteToken(
                    id=uuid.uuid4(),
                    guest_id=guest_id,
                    token_hash=token_hash,
                    expires_at=expires_at,
                    revoked=False,
                )
            )

        if guests_to_create:
            Guest.objects.bulk_create(guests_to_create, batch_size=500)
            InviteToken.objects.bulk_create(tokens_to_create, batch_size=500)
            created_count = len(guests_to_create)

    return created_count, errors


def verify_and_get_guest_by_token(raw_token: str) -> Guest | None:
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    token_obj = InviteToken.objects.filter(token_hash=token_hash).select_related("guest", "guest__event").first()
    if token_obj and token_obj.is_valid():
        return token_obj.guest
    return None
