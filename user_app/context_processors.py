"""
Custom context processors for user_app.
Session va boshqa global ma'lumotlarni templatega uzatish.
"""
from django.conf import settings


def session_settings(request):
    """
    Session sozlamalarini templatega uzatish.
    """
    return {
        'session_timeout_minutes': getattr(settings, 'SESSION_INACTIVITY_TIMEOUT', 15),
        'session_cookie_age': getattr(settings, 'SESSION_COOKIE_AGE', 1800),
    }
