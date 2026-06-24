import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from assets.models import Asset, AssetRequest, AssetRequestItem, AssetLog

# (asset name, units to add, cost per unit) — mirrors the "Add Stock" action.
STOCK_ADDITIONS = [
    ("Bond Paper (Ream)", 100, 280.00),
    ("Ballpen",           250, 15.00),
    ("Toner Cartridge",   10,  3200.00),
    ("Sticky Notes (Pad)", 80, 45.00),
    ("Highlighter",       120, 28.00),
    ("Printer",           3,   12000.00),
]


# Requests that are already approved — stock is deducted, just like the
# Approve action in the app.
APPROVED_REQUESTS = [
    {
        "requestor": "Rosalie",
        "group": "Software Engineering",
        "reason": "Replenish monthly printing supplies",
        "items": [("Bond Paper (Ream)", 10), ("Ballpen", 20)],
    },
    {
        "requestor": "Vincent",
        "group": "Helpdesk",
        "reason": "Request of team",
        "items": [("Manila Folder", 15), ("Sticky Notes (Pad)", 5)],
    },
    {
        "requestor": "Benedict",
        "group": "SysAd Team",
        "reason": "Routine office consumables",
        "items": [("Highlighter", 12), ("Correction Tape", 8)],
    },
    {
        "requestor": "Vincent",
        "group": "Communications and Training",
        "reason": "Printer maintenance and refill",
        "items": [("Toner Cartridge", 2)],
    },
    {
        "requestor": "Rosalie",
        "group": "Administration",
        "reason": "Conference room restocking",
        "items": [("Permanent Marker", 6), ("Whiteboard", 1)],
    },
    {
        "requestor": "Rosalie",
        "group": "Administration",
        "reason": "Document filing materials",
        "items": [("Manila Folder", 20), ("Paper Clips (Box)", 4)],
    },
]


# A few requests left pending, so the dashboard / request queue isn't empty.
PENDING_REQUESTS = [
    {
        "requestor": "Vincent",
        "group": "Maintenance",
        "reason": "Quarterly supply restock",
        "items": [("Glue Stick", 10), ("Scotch Tape (Roll)", 6)],
    },
    {
        "requestor": "Benedict",
        "group": "Software Engineering",
        "reason": "Additional toner",
        "items": [("Toner Cartridge", 3)],
    },
]


def get_user(username):
    return User.objects.filter(username=username).first()


def get_stock_performer():
    performer = User.objects.filter(
        username="Raymart", groups__name="Administrator"
    ).first()
    if performer is None:
        performer = User.objects.filter(groups__name="Administrator").first()
    if performer is None:
        performer = User.objects.filter(is_superuser=True).first()
    return performer


def set_request_time(request, when):
    AssetRequest.objects.filter(pk=request.pk).update(created_at=when)


def set_log_time(log, when):
    AssetLog.objects.filter(pk=log.pk).update(timestamp=when)


def add_stock():
    performer = get_stock_performer()
    now = timezone.now()
    created = 0

    for offset, (asset_name, amount, cost) in enumerate(STOCK_ADDITIONS):
        asset = Asset.objects.filter(name=asset_name).first()
        if asset is None:
            print(f"  SKIP stock: asset '{asset_name}' not found — run seed_assets.py first.")
            continue

        cost_per_unit = Decimal(str(cost))
        asset.quantity += amount
        asset.save()

        log = AssetLog.objects.create(
            asset=asset,
            action=AssetLog.ACTION_STOCK,
            performed_by=performer,
            cost_per_unit=cost_per_unit,
            notes=(
                f"Added {amount} unit(s) at \u20B1{cost_per_unit} each. "
                f"New stock: {asset.quantity}"
            ),
        )
        # Spread the history across the last few weeks (oldest first).
        set_log_time(log, now - timedelta(days=20 - offset * 3, hours=2))
        created += 1
        print(f"  Stock +{amount}: {asset.name} -> {asset.quantity} on hand")

    return created


def create_request(spec, status, when, deduct_stock):
    requestor = get_user(spec["requestor"])
    if requestor is None:
        print(f"  SKIP request: user '{spec['requestor']}' not found — run seed_users.py first.")
        return False

    with transaction.atomic():
        ar = AssetRequest.objects.create(
            requestor_name=requestor.get_full_name() or requestor.username,
            requestor_group=spec["group"],
            reason=f"{spec['reason']}",
            status=status,
            created_by=requestor,
        )

        for asset_name, qty in spec["items"]:
            asset = Asset.objects.filter(name=asset_name).first()
            if asset is None:
                print(f"    SKIP item: asset '{asset_name}' not found.")
                continue

            approved_qty = 0
            if deduct_stock:
                if asset.quantity < qty:
                    print(
                        f"    WARN: not enough stock for {asset.name} "
                        f"(need {qty}, have {asset.quantity}) — clamping."
                    )
                    qty = asset.quantity
                approved_qty = qty
                asset.quantity = max(asset.quantity - qty, 0)
                asset.save()

            AssetRequestItem.objects.create(
                request=ar,
                asset=asset,
                quantity=qty,
                approved_quantity=approved_qty,
            )

        set_request_time(ar, when)

    label = "APPROVED" if status == AssetRequest.APPROVED else "PENDING"
    print(f"  {label}: #{ar.id} {ar.requestor_name} ({ar.requestor_group})")
    return True


def main():
    now = timezone.now()

    print("Adding stock to assets...")
    stock_count = add_stock()

    print("\nCreating approved requests...")
    approved_count = 0
    for i, spec in enumerate(APPROVED_REQUESTS):
        when = now - timedelta(days=18 - i * 3, hours=1)
        if create_request(spec, AssetRequest.APPROVED, when, deduct_stock=True):
            approved_count += 1

    print("\nCreating pending requests...")
    pending_count = 0
    for i, spec in enumerate(PENDING_REQUESTS):
        when = now - timedelta(days=2 - i, hours=3)
        if create_request(spec, AssetRequest.FOR_APPROVAL, when, deduct_stock=False):
            pending_count += 1

    print(
        f"\nDone. {stock_count} stock addition(s), "
        f"{approved_count} approved request(s), "
        f"{pending_count} pending request(s) seeded."
    )


if __name__ == "__main__":
    main()
