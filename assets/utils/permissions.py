from django.contrib.auth.models import Group

def is_admin_user(user):
    return (
        user.is_superuser or
        user.groups.filter(name__in=["Administrator", "Executive"]).exists()
    )