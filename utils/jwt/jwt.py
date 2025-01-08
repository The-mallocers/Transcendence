import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings

def generate_access_token(user):
    now = datetime.now(tz=timezone.utc)
    access_payload = {
        "user_id": str(user.id),
        "exp": now + timedelta(minutes=settings.EXPIRATION_ACCESS_TOKEN),
        "iat": now,
        "session_version": str(user.session_user)
    }
    refresh_payload = {
        "user_id": str(user.id),
        "exp": now + timedelta(days=settings.EXPIRATION_REFRESH_TOKEN),
        "iat": now,
        "session_version": str(user.session_user)
    }

    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
    return access_token, refresh_token
