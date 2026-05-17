from django.contrib import admin

from .models import SystemConfig


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ('System Information', {
            'fields': ('system_name', 'version', 'founded'),
            'description': 'Configure the main system details'
        }),
        ('Content', {
            'fields': ('description', 'features'),
            'description': 'Manage the homepage content'
        }),
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_image'),
            'description': 'Customize the hero section on homepage'
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        # Only allow one SystemConfig instance
        return not SystemConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the configuration
        return False
