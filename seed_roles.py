import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import Group, Permission

# Permissions per role based on the permissions matrix.
# Keys map to Django permission codenames.
ROLE_PERMISSIONS = {
    "Administrator": [
        # Asset Management
        "view_asset",
        "request_asset",
        "approve_request",
        "add_asset",
        "change_asset",
        "delete_asset",
        "audit_assets",
        "view_dashboard",
        # Request Management
        "view_assetrequest",
        "view_pending_requests",
        "view_request_history",
        # User Management
        "view_user",
        "add_user",
        "change_user",
        "delete_user",
        # Role Management
        "view_group",
        "add_group",
        "change_group",
        "delete_group",
    ],
    "Executive": [
        # Asset Management
        "view_asset",
        "view_dashboard",
        # Request Management
        "view_assetrequest",
        "view_pending_requests",
        "view_request_history",
        # User Management
        "view_user",
        # Role Management
        "view_group",
    ],
    "Staff": [
        # Asset Management
        "view_asset",
        "request_asset",
        # Request Management
        "view_assetrequest",
        "view_request_history",
    ],
    "Approver": [
        # Asset Management
        "view_asset",
        "request_asset",
        "approve_request",
        # Request Management
        "view_assetrequest",
        "view_pending_requests",
        "view_request_history",
    ],
}


def get_permission(codename):
    try:
        return Permission.objects.get(codename=codename)
    except Permission.DoesNotExist:
        print(f"  WARNING: Permission '{codename}' not found — run migrations first.")
        return None
    except Permission.MultipleObjectsReturned:
        print(f"  WARNING: Multiple permissions found for '{codename}', skipping.")
        return None


def main():
    for role_name, codenames in ROLE_PERMISSIONS.items():
        group, created = Group.objects.get_or_create(name=role_name)

        permissions = [p for c in codenames if (p := get_permission(c)) is not None]
        group.permissions.set(permissions)

        action = "Created" if created else "Updated"
        print(f"{action} '{role_name}' with {len(permissions)} permission(s).")

    print("\nDone. All roles have been seeded.")


if __name__ == "__main__":
    main()
