from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
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
            user.is_staff = True  # Set new accounts as staff
            user.save()

            Profile.objects.create(
                user=user,
                contact_number=request.POST.get("contact_number"),
                designation=None  # No designation for new users
            )

            return redirect("assets:landing")

    return render(request, "users/register.html", {"form": form})


# User Profile 
@login_required
def user_profile(request, user_id):
    # Superusers have full access
    if not request.user.is_superuser:
        current_user_profile = getattr(request.user, 'profile', None)
        current_designation = current_user_profile.designation if current_user_profile else None
        
        # Check permissions: Admin can view anyone's profile, Staff can only view their own
        if current_designation:
            current_role_name = str(current_designation.name).lower()
            admin_roles = ['administrator', 'executive']
            
            if current_role_name not in admin_roles and request.user.id != user_id:
                return HttpResponseForbidden("You can only view your own profile.")
        else:
            return HttpResponseForbidden("You don't have permission to view profiles.")

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
    # Superusers can see all users
    if request.user.is_superuser:
        users = User.objects.all()
        can_manage_all = True
    else:
        current_user_profile = getattr(request.user, 'profile', None)
        current_designation = current_user_profile.designation if current_user_profile else None
        
        if not current_designation:
            return HttpResponseForbidden("You don't have permission to access user management.")
        
        current_role_name = str(current_designation.name).lower()
        admin_roles = ['administrator', 'executive']
        
        if current_role_name in admin_roles:
            users = User.objects.all()
            can_manage_all = True
        else:
            users = [request.user]
            can_manage_all = False

    context = {
        'users': users,
        'can_manage_all': can_manage_all
    }

    return render(
        request,
        'users/user_list.html',
        context
    )


# User Create
@login_required
def user_create(request):
    # Only superusers and admin/executive can create users
    if not request.user.is_superuser:
        current_user_profile = getattr(request.user, 'profile', None)
        current_designation = current_user_profile.designation if current_user_profile else None
        
        if not current_designation:
            return HttpResponseForbidden("You don't have permission to create users.")
        
        current_role_name = str(current_designation.name).lower()
        admin_roles = ['administrator', 'executive']
        
        if current_role_name not in admin_roles:
            return HttpResponseForbidden("Only Administrator and Executive can create users.")
    
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_staff = True  # Set new accounts as staff
            user.save()

            role_id = request.POST.get("designation")
            if role_id:
                role = Role.objects.get(id=role_id)
            else:
                role = None

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
    return render(request, "users/user_form.html", {"form": form, "roles": roles, "title": "Create User", "is_admin_editing": True})


# User Edit
@login_required
def user_edit(request, user_id):
    from .forms import UserEditForm
    
    user_to_edit = get_object_or_404(User, id=user_id)
    is_admin_editing = False
    
    # Check permissions: Superusers can edit anyone
    if request.user.is_superuser:
        is_admin_editing = True
    else:
        current_user_profile = getattr(request.user, 'profile', None)
        current_designation = current_user_profile.designation if current_user_profile else None
        
        if not current_designation:
            return HttpResponseForbidden("You don't have permission to edit users.")
        
        current_role_name = str(current_designation.name).lower()
        admin_roles = ['administrator', 'executive']
        
        # Check permissions: Admin can edit anyone, Staff can only edit themselves
        if current_role_name not in admin_roles:
            if request.user.id != user_to_edit.id:
                return HttpResponseForbidden("You can only edit your own account.")
        else:
            is_admin_editing = True
    
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            user_to_edit = form.save()
            
            contact_number = request.POST.get("contact_number", "")
            role_id = request.POST.get("designation")
            
            profile, created = Profile.objects.get_or_create(user=user_to_edit)
            profile.contact_number = contact_number
            
            # Only admin/executive/superuser can change designation, staff cannot
            if is_admin_editing and role_id:
                profile.designation = Role.objects.get(id=role_id)
            
            profile.save()
            
            return redirect("assets:user_list")
    else:
        form = UserEditForm(instance=user_to_edit)
        profile, created = Profile.objects.get_or_create(user=user_to_edit)
        form.initial['contact_number'] = profile.contact_number
        if profile.designation:
            form.initial['designation'] = profile.designation

    roles = Role.objects.all()
    return render(request, "users/user_form.html", {"form": form, "roles": roles, "title": "Edit User", "user": user_to_edit, "is_admin_editing": is_admin_editing})


# User Delete
@login_required
def user_delete(request, user_id):
    # Only superusers and admin/executive can delete users
    if not request.user.is_superuser:
        current_user_profile = getattr(request.user, 'profile', None)
        current_designation = current_user_profile.designation if current_user_profile else None
        
        if not current_designation:
            return HttpResponseForbidden("You don't have permission to delete users.")
        
        current_role_name = str(current_designation.name).lower()
        admin_roles = ['administrator', 'executive']
        
        if current_role_name not in admin_roles:
            return HttpResponseForbidden("Only Administrator and Executive can delete users. Staff cannot delete any accounts.")
    
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