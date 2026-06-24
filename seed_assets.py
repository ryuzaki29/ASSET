import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from assets.models import Asset

ASSETS = [
    {
        "name":       "Office Chair",
        "asset_type": "equipment",
        "category":   "Furniture",
        "cost":       3500.00,
        "quantity":   20,
        "status":     "Available",
        "log_details": "Ergonomic office chairs for staff workstations.",
    },
    {
        "name":       "Office Desk",
        "asset_type": "equipment",
        "category":   "Furniture",
        "cost":       6500.00,
        "quantity":   15,
        "status":     "Available",
        "log_details": "Standard office desks with cable management.",
    },
    {
        "name":       "Desktop Computer",
        "asset_type": "equipment",
        "category":   "IT Equipment",
        "cost":       35000.00,
        "quantity":   10,
        "status":     "Available",
        "log_details": "Core i5 desktop units for administrative staff.",
    },
    {
        "name":       "Laptop",
        "asset_type": "equipment",
        "category":   "IT Equipment",
        "cost":       55000.00,
        "quantity":   8,
        "status":     "Available",
        "log_details": "Portable laptops assigned to field and remote staff.",
    },
    {
        "name":       "Printer",
        "asset_type": "equipment",
        "category":   "IT Equipment",
        "cost":       12000.00,
        "quantity":   5,
        "status":     "Available",
        "log_details": "Laser printers shared across departments.",
    },
    {
        "name":       "Filing Cabinet",
        "asset_type": "equipment",
        "category":   "Furniture",
        "cost":       4800.00,
        "quantity":   12,
        "status":     "Available",
        "log_details": "4-drawer steel filing cabinets for document storage.",
    },
    {
        "name":       "Whiteboard",
        "asset_type": "equipment",
        "category":   "Office Supplies",
        "cost":       2200.00,
        "quantity":   6,
        "status":     "Available",
        "log_details": "Magnetic whiteboards for meeting rooms.",
    },
    {
        "name":       "Projector",
        "asset_type": "equipment",
        "category":   "AV Equipment",
        "cost":       25000.00,
        "quantity":   3,
        "status":     "Available",
        "log_details": "HD projectors for conference and training rooms.",
    },
    {
        "name":       "Bond Paper (Ream)",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       280.00,
        "quantity":   200,
        "status":     "Available",
        "log_details": "Short bond paper, 80gsm, for general printing use.",
    },
    {
        "name":       "Ballpen",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       15.00,
        "quantity":   500,
        "status":     "Available",
        "log_details": "Black and blue ballpens for daily office use.",
    },
    {
        "name":       "Stapler",
        "asset_type": "equipment",
        "category":   "Office Supplies",
        "cost":       350.00,
        "quantity":   25,
        "status":     "Available",
        "log_details": "Heavy-duty staplers for office documents.",
    },
    {
        "name":       "Toner Cartridge",
        "asset_type": "consumable",
        "category":   "IT Equipment",
        "cost":       3200.00,
        "quantity":   30,
        "status":     "Available",
        "log_details": "Replacement toner cartridges for laser printers.",
    },
        {
        "name":       "Sticky Notes (Pad)",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       45.00,
        "quantity":   150,
        "status":     "Available",
        "log_details": "3x3 inch sticky note pads, assorted colors.",
    },
    {
        "name":       "Manila Folder",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       12.00,
        "quantity":   300,
        "status":     "Available",
        "log_details": "Long manila folders for document filing.",
    },
    {
        "name":       "Permanent Marker",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       35.00,
        "quantity":   180,
        "status":     "Available",
        "log_details": "Fine-tip permanent markers, black.",
    },
    {
        "name":       "Highlighter",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       28.00,
        "quantity":   220,
        "status":     "Available",
        "log_details": "Assorted neon highlighters for document markup.",
    },
    {
        "name":       "Correction Tape",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       40.00,
        "quantity":   130,
        "status":     "Available",
        "log_details": "5mm correction tape rollers.",
    },
    {
        "name":       "Paper Clips (Box)",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       25.00,
        "quantity":   90,
        "status":     "Available",
        "log_details": "33mm paper clips, 100 pieces per box.",
    },
    {
        "name":       "Binder Clips (Box)",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       55.00,
        "quantity":   75,
        "status":     "Available",
        "log_details": "Assorted-size binder clips, 12 pieces per box.",
    },
    {
        "name":       "Glue Stick",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       30.00,
        "quantity":   140,
        "status":     "Available",
        "log_details": "Non-toxic 8g glue sticks.",
    },
    {
        "name":       "Scotch Tape (Roll)",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       22.00,
        "quantity":   160,
        "status":     "Available",
        "log_details": "Clear adhesive tape, 1 inch rolls.",
    },
    {
        "name":       "Envelope (Long, Pack)",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       65.00,
        "quantity":   110,
        "status":     "Available",
        "log_details": "Long white mailing envelopes, 10 pieces per pack.",
    },
    {
        "name":       "Bathroom Tissue (Roll)",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       12.00,
        "quantity":   40,
        "status":     "Available",
        "log_details": "4 rolls per pack, 2-ply bathroom tissue.",
    },

     {
        "name":       "Pranela",
        "asset_type": "consumable",
        "category":   "Office Supplies",
        "cost":       22.00,
        "quantity":   1,
        "status":     "Available",
        "log_details": "rugged pranela for bathroom use",
    },
]


def main():
    for data in ASSETS:
        asset, created = Asset.objects.get_or_create(
            name=data["name"],
            defaults={
                "asset_type":  data["asset_type"],
                "category":    data["category"],
                "cost":        data["cost"],
                "quantity":    data["quantity"],
                "status":      data["status"],
                "log_details": data["log_details"],
            },
        )

        action = "Created" if created else "Already exists"
        print(f"{action}: {asset.name} ({asset.asset_type}) — qty {asset.quantity}")

    print("\nDone. All assets have been seeded.")


if __name__ == "__main__":
    main()
