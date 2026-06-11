from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_assetrequest_assetrequestitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetrequestitem',
            name='approved_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
