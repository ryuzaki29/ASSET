from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Sum, Q

from .models import Asset
from content.models import SystemConfig


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
        }
    
    context = {
        'total_assets': total_assets,
        'total_users': total_users,
        'equipment_count': equipment_count,
        'consumable_count': consumable_count,
        'total_value': total_value,
        'recent_assets': recent_assets,
        'about': about_data,
    }
    return render(request, "assets/index.html", context)


def asset_list(request):
    assets = Asset.objects.all()
    context = {"assets": assets}
    return render(request, "assets/order_list.html", context)

def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    context = {"asset": asset}
    return render(request, "assets/order_detail.html", context)


def user_list(request):
    return render(request, "assets/user_list.html")