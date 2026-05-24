from django.db import migrations


def create_default_roles(apps, schema_editor):
    Role = apps.get_model('roles', 'Role')

    default_roles = [
        {
            'name': 'ADMINISTRATOR',
            'description': 'Has full access to the system, including user management, configuration, and all administrative functions.'
        },
        {
            'name': 'EXECUTIVE',
            'description': 'Has access to high-level reports, dashboards, and read-only views across all departments.'
        },
        {
            'name': 'STAFF',
            'description': 'Has access to standard day-to-day operations and features relevant to their assigned tasks.'
        },
    ]

    for role_data in default_roles:
        role, created = Role.objects.get_or_create(name=role_data['name'])
        role.description = role_data['description']
        role.save()


def reverse_default_roles(apps, schema_editor):
    Role = apps.get_model('roles', 'Role')
    Role.objects.filter(name__in=['ADMINISTRATOR', 'EXECUTIVE', 'STAFF']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0002_auto_20260523_2218'),
    ]

    operations = [
        migrations.RunPython(create_default_roles, reverse_default_roles),
    ]