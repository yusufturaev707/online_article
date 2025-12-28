from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class SecureAuthenticationBackend(ModelBackend):
    """
    Custom authentication backend that checks if user is blocked.
    CWE-287 fix: Proper authentication with is_blocked check.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing attacks
            User().set_password(password)
            return None

        # Check if user is blocked
        if user.is_blocked:
            return None

        # Check password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False or is_blocked=True.
        """
        is_active = getattr(user, 'is_active', None)
        is_blocked = getattr(user, 'is_blocked', False)
        return is_active and not is_blocked
