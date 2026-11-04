from .models import Users


def get_profile(user):
    if not user or not user.is_authenticated:
        return None
    try:
        return user.profile
    except Users.DoesNotExist:
        return None