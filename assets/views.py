from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .models import Asset, Profile
from assets.roles.models import Role


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

            role = Role.objects.get(id=request.POST.get("designation"))

            Profile.objects.create(
                user=user,
                contact_number=request.POST.get("contact_number"),
                designation=role
            )

            return redirect("assets:landing")

    roles = Role.objects.all()
    return render(request, "users/register.html", {"form": form, "roles": roles})


# User Profile 
@login_required
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
@login_required
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


# User Create
@login_required
def user_create(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            role_id = request.POST.get("designation")
            if role_id:
                role = Role.objects.get(id=role_id)
            else:
                role = Role.objects.first()

            contact_number = request.POST.get("contact_number", "")
            
            Profile.objects.create(
                user=user,
                contact_number=contact_number,
                designation=role
            )

            return redirect("assets:user_list")
    else:
        form = UserRegistrationForm()

    roles = Role.objects.all()
    return render(request, "users/user_form.html", {"form": form, "roles": roles, "title": "Create User"})


# User Edit
@login_required
def user_edit(request, user_id):
    from .forms import UserEditForm
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            
            contact_number = request.POST.get("contact_number", "")
            role_id = request.POST.get("designation")
            
            profile = Profile.objects.get(user=user)
            profile.contact_number = contact_number
            
            if role_id:
                profile.designation = Role.objects.get(id=role_id)
            
            profile.save()
            
            return redirect("assets:user_list")
    else:
        form = UserEditForm(instance=user)
        if hasattr(user, 'profile'):
            form.initial['contact_number'] = user.profile.contact_number
            form.initial['designation'] = user.profile.designation

    roles = Role.objects.all()
    return render(request, "users/user_form.html", {"form": form, "roles": roles, "title": "Edit User", "user": user})


# User Delete
@login_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        user.delete()
        return redirect("assets:user_list")
    
    return render(request, "users/user_confirm_delete.html", {"user": user})

def index(request):
    return render(request, "assets/index.html")


@login_required
def asset_list(request):
    assets = Asset.objects.all()
    context = {"assets": assets}
    return render(request, "assets/order_list.html", context)

@login_required
def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    context = {"asset": asset}
    return render(request, "assets/order_detail.html", context)

@login_required
def asset_create(request):
    if request.method == "POST":
        asset = Asset(
            name=request.POST.get("name"),
            asset_type=request.POST.get("asset_type"),
            category=request.POST.get("category"),
            cost=request.POST.get("cost"),
            quantity=request.POST.get("quantity"),
            status=request.POST.get("status"),
            log_details=request.POST.get("log_details", "")
        )
        asset.save()
        return redirect("assets:asset_list")
    
    context = {
        "type_choices": Asset.TYPE_CHOICES
    }
    return render(request, "assets/create_asset.html", context)

@login_required
def asset_edit(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    
    if request.method == "POST":
        asset.name = request.POST.get("name")
        asset.asset_type = request.POST.get("asset_type")
        asset.category = request.POST.get("category")
        asset.cost = request.POST.get("cost")
        asset.quantity = request.POST.get("quantity")
        asset.status = request.POST.get("status")
        asset.log_details = request.POST.get("log_details", "")
        asset.save()
        return redirect("assets:asset_detail", asset_id=asset.id)
    
    context = {
        "asset": asset,
        "type_choices": Asset.TYPE_CHOICES
    }
    return render(request, "assets/edit_asset.html", context)