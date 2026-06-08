from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import TemplateView
from .forms import UserRegistrationForm, UserEditForm 
from .models import Asset, Profile
from django.contrib.auth.mixins import PermissionRequiredMixin


def can_view_all_users(user):
    return (
        user.is_superuser or
        user.has_perm("auth.view_user")
    )

def can_add_users(user):
    return (
        user.is_superuser or
        user.has_perm("auth.add_user")
    )

def can_change_users(user):
    return (
        user.is_superuser or
        user.has_perm("auth.change_user")
    )

def can_delete_users(user):
    return (
        user.is_superuser or
        user.has_perm("auth.delete_user")
    )

def landing(request):
    return render(request, "assets/landing.html")

# Added Registration Form
def register_view(request):
    form = UserRegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.is_staff = True
        user.save()

        Profile.objects.create(user=user)

        return redirect("assets:landing")

    return render(
            request,
            "users/register.html",
            {"form": form}
        )

# User Profile 
@login_required
def user_profile(request, user_id):

    if (
        request.user.id != user_id and
        not can_view_all_users(request.user)
    ):
        return HttpResponseForbidden(
            "You do not have permission to view this profile."
        )

    user = get_object_or_404(
        User,
        id=user_id
    )

    return render(
        request,
        "users/user_profile.html",
        {
            "profile_user": user
        }
    )

# User List
@login_required
def user_list(request):

    if can_view_all_users(request.user):
        users = User.objects.all()
        can_manage_all = True

    else:
        users = [request.user]
        can_manage_all = False

    return render(
        request,
        "users/user_list.html",
        {
            "users": users,
            "can_manage_all": can_manage_all
        }
    )


# User Create
@login_required
def user_create(request):

    if not can_add_users(request.user):
        return HttpResponseForbidden(
            "You do not have permission to create users."
        )

    form = UserRegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.is_staff = True
        user.save()

        Profile.objects.create(user=user)

        group_id = request.POST.get("group")

        if group_id:
            group = get_object_or_404(Group, id=group_id)
            user.groups.add(group)

        return redirect("assets:user_list")

    groups = Group.objects.all().order_by("name")

    return render(
        request,
        "users/user_form.html",
        {
            "form": form,
            "groups": groups,
            "title": "Create User",
            "can_manage_groups": True
        }
    )

# User Edit
@login_required
def user_edit(request, user_id):

    user_to_edit = get_object_or_404(User, id=user_id)

    can_manage_groups = can_change_users(request.user)

    if (
        not can_manage_groups and
        request.user.id != user_to_edit.id
    ):
        return HttpResponseForbidden(
            "You can only edit your own account."
        )

    if request.method == "POST":
        form = UserEditForm(
            request.POST,
            instance=user_to_edit
        )

        if form.is_valid():
            form.save()
            return redirect("assets:user_list")

    else:
        form = UserEditForm(instance=user_to_edit)

    return render(
        request,
        "users/user_form.html",
        {
            "form": form,
            "title": "Edit User",
            "user": user_to_edit,
            "can_manage_groups": can_manage_groups,
        }
    )

# User Delete
@login_required
def user_delete(request, user_id):

    if not can_delete_users(request.user):
        return HttpResponseForbidden(
            "You do not have permission to delete users."
        )

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.delete()
        return redirect("assets:user_list")

    return render(
        request,
        "users/user_confirm_delete.html",
        {"user": user}
    )


class IndexView(TemplateView):
    template_name = "assets/index.html"

# Asset Views
@login_required
@permission_required("assets.view_asset", raise_exception=True)
def asset_list(request):
    assets = Asset.objects.all()
    context = {"assets": assets}
    return render(request, "assets/order_list.html", context)

# Asset Detail
@login_required
@permission_required("assets.view_asset", raise_exception=True)
def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    context = {"asset": asset}
    return render(request, "assets/order_detail.html", context)

# Asset Create
@login_required
@permission_required("assets.add_asset", raise_exception=True)
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

# Asset Edit
@login_required
@permission_required("assets.change_asset", raise_exception=True)
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


