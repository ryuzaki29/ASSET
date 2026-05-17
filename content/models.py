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
    hero_title = models.CharField(
        max_length=200,
        default='Asset Management that makes a difference',
        help_text='Main headline for hero section'
    )
    hero_subtitle = models.TextField(
        default='Streamline your asset tracking, enhance inventory control, and maximize operational efficiency with our comprehensive platform designed for modern businesses.',
        help_text='Subtitle/description for hero section'
    )
    hero_image = models.ImageField(
        upload_to='hero/',
        blank=True,
        null=True,
        help_text='Hero section image displayed on homepage (right side box)'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.system_name

    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configuration"
