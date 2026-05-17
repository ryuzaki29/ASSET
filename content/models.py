from django.db import models


class SystemConfig(models.Model):
    """Global system configuration and content management."""
    system_name = models.CharField(
        max_length=200,
        default='RAYMART Asset Management System',
        help_text='The name of your system'
    )
    version = models.CharField(
        max_length=50,
        default='1.0.0',
        help_text='Current system version'
    )
    description = models.TextField(
        default='A comprehensive solution for managing company assets efficiently',
        help_text='System description displayed on homepage'
    )
    features = models.TextField(
        default='Real-time asset tracking\nUser management\nAsset categorization\nInventory valuation\nAdmin dashboard',
        help_text='Key features (one per line)'
    )
    founded = models.CharField(
        max_length=50,
        default='2026',
        help_text='Year or date founded'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.system_name

    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configuration"
