from django.db import migrations

def create_default_roles(apps, schema_editor):
    Role = apps.get_model('roles', 'Role')
    # This automatically injects the 3 roles into your database table
    Role.objects.get_or_create(name='ADMIN', description='System Administrator')
    Role.objects.get_or_create(name='EXEC', description='Executive User')
    Role.objects.get_or_create(name='STAFF', description='Regular Staff Member')

class Migration(migrations.Migration):

    dependencies = [
        # This will automatically point to your previous migration file
        ('roles', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(create_default_roles),
    ]