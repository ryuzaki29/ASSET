import os
from datetime import datetime, timezone

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

try:
    from assets.models import MenuItem, Order  # noqa: E402
except ImportError as exc:
    raise SystemExit(
        "Could not import Order. Add the Order model and run migrations before "
        "running this script."
    ) from exc


EXPECTED_ORDER_FIELDS = {"menu_item", "quantity", "ordered_at", "waiter", "is_discounted"}
OLD_ORDER_FIELD_NAMES = {
    "date": "ordered_at",
    "person": "waiter",
}


SAMPLE_ORDERS = [
    {
        "waiter": "Ana Santos",
        "menu_item": "Chicken Adobo",
        "quantity": 5,
        "is_discounted": False,
        "ordered_at": datetime(2026, 5, 2, 0, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Ben Cruz",
        "menu_item": "Lumpiang Shanghai",
        "quantity": 5,
        "is_discounted": True,
        "ordered_at": datetime(2026, 5, 2, 20, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Carlo Reyes",
        "menu_item": "Pancit Canton",
        "quantity": 1,
        "is_discounted": False,
        "ordered_at": datetime(2026, 5, 3, 0, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Dina Garcia",
        "menu_item": "Halo-Halo",
        "quantity": 3,
        "is_discounted": True,
        "ordered_at": datetime(2026, 5, 3, 18, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Elena Lim",
        "menu_item": "Chicken Adobo",
        "quantity": 1,
        "is_discounted": True,
        "ordered_at": datetime(2026, 5, 4, 16, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Ana Santos",
        "menu_item": "Lumpiang Shanghai",
        "quantity": 2,
        "is_discounted": False,
        "ordered_at": datetime(2026, 5, 4, 22, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Ben Cruz",
        "menu_item": "Pancit Canton",
        "quantity": 4,
        "is_discounted": False,
        "ordered_at": datetime(2026, 5, 5, 2, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Carlo Reyes",
        "menu_item": "Halo-Halo",
        "quantity": 2,
        "is_discounted": True,
        "ordered_at": datetime(2026, 5, 5, 5, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Dina Garcia",
        "menu_item": "Chicken Adobo",
        "quantity": 3,
        "is_discounted": False,
        "ordered_at": datetime(2026, 5, 5, 10, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Elena Lim",
        "menu_item": "Lumpiang Shanghai",
        "quantity": 6,
        "is_discounted": True,
        "ordered_at": datetime(2026, 5, 5, 13, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Ana Santos",
        "menu_item": "Pancit Canton",
        "quantity": 2,
        "is_discounted": False,
        "ordered_at": datetime(2026, 5, 5, 17, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Ben Cruz",
        "menu_item": "Halo-Halo",
        "quantity": 5,
        "is_discounted": False,
        "ordered_at": datetime(2026, 5, 6, 1, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Carlo Reyes",
        "menu_item": "Chicken Adobo",
        "quantity": 2,
        "is_discounted": True,
        "ordered_at": datetime(2026, 5, 6, 4, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Dina Garcia",
        "menu_item": "Lumpiang Shanghai",
        "quantity": 1,
        "is_discounted": False,
        "ordered_at": datetime(2026, 5, 6, 9, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Elena Lim",
        "menu_item": "Pancit Canton",
        "quantity": 3,
        "is_discounted": True,
        "ordered_at": datetime(2026, 5, 6, 12, 45, 19, 960323, tzinfo=timezone.utc),
    },
    {
        "waiter": "Ana Santos",
        "menu_item": "Halo-Halo",
        "quantity": 4,
        "is_discounted": False,
        "ordered_at": datetime(2026, 5, 6, 15, 45, 19, 960323, tzinfo=timezone.utc),
    },
]


def check_order_fields():
    actual_fields = {field.name for field in Order._meta.fields}
    missing_fields = EXPECTED_ORDER_FIELDS - actual_fields

    if not missing_fields:
        return

    lines = [
        "The Order model does not have the field names this seed script expects.",
        "",
        f"Expected fields: {', '.join(sorted(EXPECTED_ORDER_FIELDS))}",
        f"Found fields: {', '.join(sorted(actual_fields))}",
        "",
    ]

    old_fields = sorted(set(OLD_ORDER_FIELD_NAMES) & actual_fields)
    if old_fields:
        lines.append("It looks like you may still be using older field names:")
        for old_field in old_fields:
            lines.append(f"- Rename Order.{old_field} to Order.{OLD_ORDER_FIELD_NAMES[old_field]}")
        lines.append("")

    lines.extend(
        [
            "Update orders/models.py, run migrations, then run this script again.",
        ]
    )
    raise SystemExit("\n".join(lines))


def main():
    check_order_fields()

    menu_items = {
        menu_item.name: menu_item
        for menu_item in MenuItem.objects.filter(
            name__in=[order["menu_item"] for order in SAMPLE_ORDERS]
        )
    }

    orders = []
    for sample_order in SAMPLE_ORDERS:
        menu_item = menu_items.get(sample_order["menu_item"])
        if menu_item is None:
            raise SystemExit(f"Missing menu item: {sample_order['menu_item']}")

        orders.append(
            Order(
                waiter=sample_order["waiter"],
                menu_item=menu_item,
                quantity=sample_order["quantity"],
                is_discounted=sample_order["is_discounted"],
                ordered_at=sample_order["ordered_at"],
            )
        )

    Order.objects.bulk_create(orders)
    print(f"Added {len(orders)} sample orders.")


if __name__ == "__main__":
    main()
