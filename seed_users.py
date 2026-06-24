import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User, Group

USERS = [
    {
        "username":   "Joper",
        "first_name": "Joper",
        "last_name":  "Cunanan",
        "email":      "jlcunanan1@up.edu.ph",
        "password":   "123456",
        "role":       "Administrator",
    },
    {
        "username":   "Ada",
        "first_name": "Ada Angeli",
        "last_name":  "Cariaga",
        "email":      "adcariaga@up.edu.ph",
        "password":   "123456",
        "role":       "Administrator",
    },
    {
        "username":   "Raymart",
        "first_name": "Raymart",
        "last_name":  "Sablad",
        "email":      "rsablad@up.edu.ph",
        "password":   "123456",
        "role":       "Administrator",
    },
    {
        "username":   "Mark",
        "first_name": "Mark Jason",
        "last_name":  "Ellazar",
        "email":      "mdellazar@up.edu.ph",
        "password":   "123456",
        "role":       "Administrator",
    },
    {
        "username":   "Nanette",
        "first_name": "Nanette",
        "last_name":  "Baris",
        "email":      "nsbaris@up.edu.ph",
        "password":   "123456",
        "role":       "Administrator",
    },
    {
        "username":   "Karlo",
        "first_name": "James Karlo",
        "last_name":  "Abina",
        "email":      "joabina@up.edu.ph",
        "password":   "123456",
        "role":       "Administrator",
    },

    # --- Staff ---
    {
        "username":   "Rosalie",
        "first_name": "Rosalie",
        "last_name":  "Lazarte",
        "email":      "rlazarte@up.edu.ph",
        "password":   "123456",
        "role":       "Staff",
    },
    {
        "username":   "Vincent",
        "first_name": "Vincent",
        "last_name":  "Merioles",
        "email":      "vmerioles@up.edu.ph",
        "password":   "123456",
        "role":       "Staff",
    },
    {
        "username":   "Benedict",
        "first_name": "Benedict",
        "last_name":  "Caligayan",
        "email":      "bcaligayan@up.edu.ph",
        "password":   "123456",
        "role":       "Staff",
    },
    {
        "username":   "Elias",
        "first_name": "Elias",
        "last_name":  "Tan",
        "email":      "etan@up.edu.ph",
        "password":   "123456",
        "role":       "Staff",
    },
    {
        "username":   "Faith",
        "first_name": "Faith",
        "last_name":  "Gonzales",
        "email":      "fgonzales@up.edu.ph",
        "password":   "123456",
        "role":       "Staff",
    },

    # --- Approvers ---
    {
        "username":   "Jannine",
        "first_name": "Jannine",
        "last_name":  "Miranda",
        "email":      "jmiranda@up.edu.ph",
        "password":   "123456",
        "role":       "Approver",
    },
    {
        "username":   "Kristine",
        "first_name": "Kristine",
        "last_name":  "Agtarap",
        "email":      "kagtarap@up.edu.ph",
        "password":   "123456",
        "role":       "Approver",
    },

]


def main():
    for data in USERS:
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={
                "first_name": data["first_name"],
                "last_name":  data["last_name"],
                "email":      data["email"],
                "is_staff":   True,
            },
        )

        if created:
            user.set_password(data["password"])
            user.save()
            action = "Created"
        else:
            action = "Already exists"

        try:
            group = Group.objects.get(name=data["role"])
            user.groups.set([group])
            role_label = data["role"]
        except Group.DoesNotExist:
            role_label = f"(role '{data['role']}' not found — run seed_roles.py first)"

        print(f"{action}: {user.username} ({user.get_full_name()}) -> {role_label}")

    print("\nDone. All users have been seeded.")


if __name__ == "__main__":
    main()
