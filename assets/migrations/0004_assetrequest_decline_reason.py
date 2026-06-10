from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_assetrequestitem_approved_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetrequest',
            name='decline_reason',
            field=models.TextField(blank=True, default=''),
        ),
    ]
