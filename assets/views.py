from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .forms import UserRegistrationForm, UserEditForm 
from .models import Asset, Profile, AssetRequest, AssetRequestItem
from assets.roles.models import Role
from django.db import transaction

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
    if not request.user.is_superuser:
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.designation is None:
            return HttpResponseForbidden("Not allowed.")

        if profile.designation.name.lower() not in ['administrator', 'executive']:
            return HttpResponseForbidden("Not allowed.")

    form = UserRegistrationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_staff = True
            user.save()

            # now FIXED role handling
            role_id = request.POST.get("designation")

            role = Role.objects.get(id=role_id) if role_id else None

            Profile.objects.create(
                user=user,
                designation=role
            )

            return redirect("assets:user_list")

    roles = Role.objects.all()

    return render(request, "users/user_form.html", {
        "form": form,
        "roles": roles,
        "title": "Create User",
        "is_admin_editing": True
    })

# User Edit
@login_required
def user_edit(request, user_id):
    
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
            
            role_id = request.POST.get("designation")
            
            profile, created = Profile.objects.get_or_create(user=user_to_edit)
            
            # Only admin/executive/superuser can change designation, staff cannot
            if is_admin_editing and role_id:
                profile.designation = Role.objects.get(id=role_id)
            
            profile.save()
            
            return redirect("assets:user_list")
    else:
        form = UserEditForm(instance=user_to_edit)
        profile, created = Profile.objects.get_or_create(user=user_to_edit)

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


class IndexView(TemplateView):
    template_name = "assets/index.html"


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
        messages.success(request, "Asset created successfully.")
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
        messages.success(request, "Asset updated successfully.")
        return redirect("assets:asset_detail", asset_id=asset.id)
    
    context = {
        "asset": asset,
        "type_choices": Asset.TYPE_CHOICES
    }
    return render(request, "assets/edit_asset.html", context)


@login_required
def request_list(request):
    """List requests that are currently 'For Approval' and show all requests in history."""
    pending = AssetRequest.objects.filter(status=AssetRequest.FOR_APPROVAL).prefetch_related('items__asset').order_by('-created_at')
    history = AssetRequest.objects.prefetch_related('items__asset').order_by('-created_at')
    context = {
        'requests': pending,
        'history': history
    }
    return render(request, 'assets/request_list.html', context)


@login_required
def request_create(request):
    if request.method == "POST":
        # Collect basic fields
        requestor_name = request.POST.get('requestorName') or request.POST.get('requestor_name')
        requestor_group = request.POST.get('requestorGroup') or request.POST.get('requestor_group')
        reason = request.POST.get('requestReason') or request.POST.get('request_reason')

        with transaction.atomic():
            ar = AssetRequest.objects.create(
                requestor_name=requestor_name or (request.user.get_full_name() or request.user.username),
                requestor_group=requestor_group or "",
                reason=reason or "",
                status=AssetRequest.FOR_APPROVAL,
                created_by=request.user
            )

            # asset_select[] and asset_qty[] come from the modal form; use getlist
            asset_ids = request.POST.getlist('asset_select[]') or request.POST.getlist('asset_select')
            qtys = request.POST.getlist('asset_qty[]') or request.POST.getlist('asset_qty')

            # pair and create items
            for i, a_id in enumerate(asset_ids):
                try:
                    asset = Asset.objects.get(id=int(a_id))
                except Exception:
                    continue
                try:
                    q = int(qtys[i]) if i < len(qtys) and qtys[i] else 1
                except Exception:
                    q = 1
                if q <= 0:
                    q = 1
                AssetRequestItem.objects.create(request=ar, asset=asset, quantity=q)

        messages.success(request, "Your request has been submitted successfully.")
        return redirect('assets:asset_list')

    return redirect('assets:asset_list')


@login_required
def request_approve(request, request_id):
    if request.method != 'POST':
        return redirect('assets:request_list')

    ar = get_object_or_404(AssetRequest, id=request_id)

    if ar.status != AssetRequest.FOR_APPROVAL:
        return redirect('assets:request_list')

    insufficient_items = []
    for it in ar.items.select_related('asset'):
        asset = it.asset
        if asset.quantity < it.quantity:
            insufficient_items.append(
                f"{asset.name} (requested {it.quantity}, available {asset.quantity})"
            )

    if insufficient_items:
        messages.error(
            request,
            "Cannot approve request because the following items do not have enough stock: "
            + ", ".join(insufficient_items)
        )
        return redirect('assets:request_list')

    with transaction.atomic():
        for it in ar.items.select_related('asset'):
            asset = it.asset
            current_qty = int(asset.quantity or 0)
            decrement = int(it.quantity or 0)
            asset.quantity = max(current_qty - decrement, 0)
            asset.save()

            it.approved_quantity = decrement
            it.save()

        ar.status = AssetRequest.APPROVED
        ar.save()

    messages.success(request, "Request approved and inventory updated.")
    return redirect('assets:request_list')


@login_required
def request_decline(request, request_id):
    if request.method != 'POST':
        return redirect('assets:request_list')

    ar = get_object_or_404(AssetRequest, id=request_id)
    decline_reason = request.POST.get('decline_reason', '').strip()

    if ar.status == AssetRequest.FOR_APPROVAL:
        ar.status = AssetRequest.DECLINED
        ar.decline_reason = decline_reason
        ar.save()
        messages.success(request, "Request declined." + (" Reason saved." if decline_reason else ""))
    else:
        messages.error(request, "Only pending requests may be declined.")

    return redirect('assets:request_list')


