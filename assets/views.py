from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import TemplateView
from .forms import UserRegistrationForm, UserEditForm 
from .models import Asset, AssetRequest, AssetRequestItem, AssetLog, Profile
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
from django.contrib.auth.models import User, Group

def register_view(request):
    form = UserRegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.is_staff = True
        user.save()

        Profile.objects.create(user=user)

        # Automatically assign Staff role
        staff_group, created = Group.objects.get_or_create(
            name="Staff"
        )
        user.groups.add(staff_group)

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

    is_admin_editing = can_manage_groups or request.user.is_superuser

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
            "is_admin_editing": is_admin_editing,   # ✅ ADD THIS
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
    assets   = Asset.objects.all()
    all_logs = AssetLog.objects.select_related('asset', 'performed_by').order_by('-timestamp')
    context  = {"assets": assets, "all_logs": all_logs}
    return render(request, "assets/order_list.html", context)

# Asset Detail
@login_required
@permission_required("assets.view_asset", raise_exception=True)
def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    logs  = asset.logs.select_related('performed_by').order_by('-timestamp')
    context = {"asset": asset, "logs": logs}
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
        AssetLog.objects.create(
            asset=asset,
            action=AssetLog.ACTION_CREATED,
            performed_by=request.user,
            cost_per_unit=asset.cost,
            notes=f"Asset created with quantity {asset.quantity} at ₱{asset.cost} per unit."
        )
        messages.success(request, "Asset created successfully.")
        return redirect("assets:asset_list")
    
    context = {
        "type_choices": Asset.TYPE_CHOICES
    }
    return render(request, "assets/create_asset.html", context)

# Asset Logs JSON
@login_required
@permission_required("assets.view_asset", raise_exception=True)
def asset_logs_json(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    logs  = asset.logs.select_related('performed_by').order_by('-timestamp')
    data  = []
    for log in logs:
        if log.performed_by:
            performer = log.performed_by.get_full_name() or log.performed_by.username
        else:
            performer = '—'
        data.append({
            'timestamp':    log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'action':       log.action,
            'performed_by': performer,
            'cost_per_unit': str(log.cost_per_unit) if log.cost_per_unit else None,
            'notes':        log.notes or '—',
        })
    return JsonResponse({'asset_name': asset.name, 'logs': data})

# Asset Add Stock
@login_required
@permission_required("assets.change_asset", raise_exception=True)
def asset_add_stock(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    if request.method == "POST":
        try:
            amount = int(request.POST.get("amount", 0))
        except ValueError:
            amount = 0
        if amount > 0:
            from decimal import Decimal, InvalidOperation
            cost_str = request.POST.get("cost", "").strip()
            try:
                cost_per_unit = Decimal(cost_str) if cost_str else None
            except InvalidOperation:
                cost_per_unit = None

            asset.quantity += amount
            asset.save()

            cost_note = f" at ₱{cost_per_unit} each" if cost_per_unit else ""
            AssetLog.objects.create(
                asset=asset,
                action=AssetLog.ACTION_STOCK,
                performed_by=request.user,
                cost_per_unit=cost_per_unit,
                notes=f"Added {amount} unit(s){cost_note}. New stock: {asset.quantity}."
            )
            messages.success(request, f"Added {amount} unit(s) to {asset.name}. New stock: {asset.quantity}.")
        else:
            messages.error(request, "Please enter a valid amount greater than 0.")
    return redirect("assets:asset_list")

# Asset Edit
@login_required
@permission_required("assets.change_asset", raise_exception=True)
def asset_edit(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    
    if request.method == "POST":
        old = {
            "name": asset.name, "category": asset.category,
            "cost": str(asset.cost), "quantity": asset.quantity,
            "status": asset.status, "asset_type": asset.asset_type,
        }
        asset.name        = request.POST.get("name")
        asset.asset_type  = request.POST.get("asset_type")
        asset.category    = request.POST.get("category")
        asset.cost        = request.POST.get("cost")
        asset.quantity    = request.POST.get("quantity")
        asset.status      = request.POST.get("status")
        asset.log_details = request.POST.get("log_details", "")
        asset.save()

        changes = []
        if old["name"]      != asset.name:             changes.append(f"Name: '{old['name']}' → '{asset.name}'")
        if old["category"]  != asset.category:         changes.append(f"Category: '{old['category']}' → '{asset.category}'")
        if old["cost"]      != str(asset.cost):        changes.append(f"Cost: {old['cost']} → {asset.cost}")
        if str(old["quantity"]) != str(asset.quantity):changes.append(f"Quantity: {old['quantity']} → {asset.quantity}")
        if old["status"]    != asset.status:           changes.append(f"Status: '{old['status']}' → '{asset.status}'")
        if old["asset_type"]!= asset.asset_type:       changes.append(f"Type: '{old['asset_type']}' → '{asset.asset_type}'")

        AssetLog.objects.create(
            asset=asset,
            action=AssetLog.ACTION_EDITED,
            performed_by=request.user,
            notes="; ".join(changes) if changes else "No fields changed."
        )
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


