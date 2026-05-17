from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Sum, Q

from .models import Asset
from content.models import SystemConfig, Feature


def landing(request):
    return render(request, "assets/landing.html")

# Added Registration Form
def register_view(request):
    form = UserCreationForm()
    return render(request, "registration/user_registration.html", {"form":form})

def index(request):
    total_assets = Asset.objects.count()
    total_users = User.objects.count()
    equipment_count = Asset.objects.filter(asset_type='equipment').count()
    consumable_count = Asset.objects.filter(asset_type='consumable').count()
    total_value = Asset.objects.aggregate(Sum('cost'))['cost__sum'] or 0
    
    # Get recent assets for history
    recent_assets = Asset.objects.all().order_by('-id')[:5]
    
    # Get system configuration from database
    system_config = SystemConfig.objects.first()
    
    # Prepare about data from database or use defaults
    if system_config:
        about_data = {
            'system_name': system_config.system_name,
            'version': system_config.version,
            'description': system_config.description,
            'features': system_config.features.split('\n'),
            'founded': system_config.founded,
            'hero_title': system_config.hero_title,
            'hero_subtitle': system_config.hero_subtitle,
            'hero_image': system_config.hero_image,
            'hero_background_color': system_config.hero_background_color,
            'hero_background_image': system_config.hero_background_image,
            'metrics_section_title': system_config.metrics_section_title,
            'recent_assets_section_title': system_config.recent_assets_section_title,
        }
    else:
        # Fallback to default values if no config exists
        about_data = {
            'system_name': 'RAYMART Asset Management System',
            'version': '1.0.0',
            'description': 'A comprehensive solution for managing company assets efficiently',
            'features': [
                'Real-time asset tracking',
                'User management',
                'Asset categorization',
                'Inventory valuation',
                'Admin dashboard'
            ],
            'founded': '2026',
            'hero_title': 'Asset Management that makes a difference',
            'hero_subtitle': 'Streamline your asset tracking, enhance inventory control, and maximize operational efficiency with our comprehensive platform designed for modern businesses.',
            'hero_image': None,
            'hero_background_color': '#8a1538',
            'hero_background_image': None,
            'metrics_section_title': 'Key Metrics',
            'recent_assets_section_title': 'Recent Assets',
        }
    
    # Get active features for 'Why Choose Our System' section
    system_features = Feature.objects.filter(is_active=True).order_by('order')
    
    context = {
        'total_assets': total_assets,
        'total_users': total_users,
        'equipment_count': equipment_count,
        'consumable_count': consumable_count,
        'total_value': total_value,
        'recent_assets': recent_assets,
        'about': about_data,
        'system_features': system_features,
    }
    return render(request, "assets/index.html", context)


def asset_list(request):
    assets = Asset.objects.all().order_by('-created_at')
    total_assets = Asset.objects.count()
    equipment_count = Asset.objects.filter(asset_type='equipment').count()
    consumable_count = Asset.objects.filter(asset_type='consumable').count()
    total_value = Asset.objects.aggregate(Sum('cost'))['cost__sum'] or 0
    
    context = {
        "assets": assets,
        "total_assets": total_assets,
        "equipment_count": equipment_count,
        "consumable_count": consumable_count,
        "total_value": total_value,
    }
    return render(request, "assets/order_list.html", context)

def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    context = {"asset": asset}
    return render(request, "assets/order_detail.html", context)


def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    context = {
        "users": users,
        "total_users": total_users,
        "active_users": active_users,
        "staff_users": staff_users,
    }
    return render(request, "assets/user_list.html", context)


def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    context = {"user": user}
    return render(request, "assets/user_detail.html", context)