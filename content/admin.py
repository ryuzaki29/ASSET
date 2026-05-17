from django.contrib import admin

from .models import SystemConfig, Feature


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


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'icon', 'is_active', 'updated_at')
    list_display_links = ('title',)
    list_filter = ('is_active', 'updated_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'order')
    ordering = ('order',)
    
    fieldsets = (
        ('Feature Information', {
            'fields': ('title', 'description', 'icon'),
            'description': 'Configure feature display'
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'description': 'Control feature visibility and order'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
