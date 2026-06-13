import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import seed_roles
import seed_users
import seed_assets

print("=== Seeding Roles ===")
seed_roles.main()

print("\n=== Seeding Users ===")
seed_users.main()

print("\n=== Seeding Assets ===")
seed_assets.main()
