from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from .models import Asset, Profile


def landing(request):
    return render(request, "assets/landing.html")

# Added Registration Form
def register_view(request):

    form = UserRegistrationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            Profile.objects.create(
                user=user,
                contact_number=request.POST.get("contact_number"),
                designation=request.POST.get("designation")
            )

            return redirect("assets:landing.html")

    return render(request, "users/register.html", {"form": form})

# User Profile 
def user_profile(request, user_id):

    user = get_object_or_404(User, id=user_id)

    context = {
        'profile_user': user
    }

    return render(
        request,
        'users/user_profile.html',
        context
    )

# User List
def user_list(request):

    users = User.objects.all()

    context = {
        'users': users
    }

    return render(
        request,
        'users/user_list.html',
        context
    )

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