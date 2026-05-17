#!/usr/bin/env python
"""
Seed script to populate initial features for the system.
Run with: python manage.py shell < seed_features.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from content.models import Feature

# Delete existing features
Feature.objects.all().delete()

# Create initial features
features_data = [
    {
        'title': 'Real-time Tracking',
        'description': 'Monitor your assets in real-time with live updates and instant notifications',
        'icon': 'bi-lightning',
        'order': 0,
    },
    {
        'title': 'Secure Management',
        'description': 'Enterprise-grade security with role-based access control and audit logs',
        'icon': 'bi-shield-check',
        'order': 1,
    },
    {
        'title': 'Analytics & Reports',
        'description': 'Comprehensive insights with detailed reports and data visualization',
        'icon': 'bi-graph-up',
        'order': 2,
    },
    {
        'title': 'User Management',
        'description': 'Easy user administration with flexible permission settings',
        'icon': 'bi-person-check',
        'order': 3,
    },
    {
        'title': 'Asset Categorization',
        'description': 'Organize assets by type, category, and status for better control',
        'icon': 'bi-layers',
        'order': 4,
    },
    {
        'title': '24/7 Support',
        'description': 'Dedicated support team ready to help you succeed',
        'icon': 'bi-headset',
        'order': 5,
    },
]

for feature_data in features_data:
    feature = Feature.objects.create(**feature_data)
    print(f'✓ Created feature: {feature.title}')

print(f'\n✓ Successfully seeded {len(features_data)} features!')
