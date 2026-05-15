from django.shortcuts import render, get_object_or_404

from .models import Asset


def landing(request):
    return render(request, "assets/landing.html")


def index(request):
    return render(request, "assets/index.html")


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