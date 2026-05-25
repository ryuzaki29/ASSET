from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from .forms import UserEditForm

from .models import Asset


def landing(request):
    return render(request, "assets/landing.html")

def register_view(request):

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = CustomUserCreationForm()

    return render(request, "registration/user_registration.html", {"form": form})

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
    users = User.objects.all()

    context = {
        "users": users
    }

    return render(request, "assets/user_list.html", context)

def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return redirect("assets:user_list")

    else:
        form = UserEditForm(instance=user)

    return render(request, "assets/user_edit.html", {"form": form})