from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from .forms import UserRegistrationForm, UserEditForm
from .models import Asset, AssetRequest, AssetRequestItem, AssetLog, Profile
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q

from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper, Q
from decimal import Decimal

class CustomLoginView(LoginView):
    def form_valid(self, form):
        user = form.get_user()
        if not user.groups.exists():
            messages.warning(
                self.request,
                "Your account does not have a role assigned yet. Please contact an administrator."
            )
            return redirect("login")
        return super().form_valid(form)


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

@login_required
def placeholder_view(request):
    return render(request, "assets/placeholder.html")

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

        messages.success(request, "Account registered successfully! Please wait for an administrator to assign your role before you can log in.")
        return redirect("login")

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

    user_requests = AssetRequestItem.objects.filter(
        request__created_by=user
    ).select_related(
        'asset',
        'request'
    )

    search = request.GET.get('search', '').strip()

    if search:
        user_requests = user_requests.filter(
            asset__name__icontains=search
        )

    user_requests = user_requests.order_by(
        '-request__created_at'
    )

    paginator = Paginator(user_requests, 10)
    page_number = request.GET.get('page')
    user_requests = paginator.get_page(page_number)

    return render(
        request,
        "users/user_profile.html",
        {
            "profile_user": user,
            "requests": user_requests,
            "search": search,
        }
    )

# User List
@login_required
def user_list(request):

    if not can_view_all_users(request.user):
        return HttpResponseForbidden(
            "You do not have permission to view users."
        )

    assigned_users = User.objects.filter(groups__isnull=False).distinct()
    new_users = User.objects.filter(groups__isnull=True)

    return render(
        request,
        "users/user_list.html",
        {
            "assigned_users": assigned_users,
            "new_users": new_users,
            "total_users": assigned_users.count() + new_users.count(),
            "can_manage_all": True
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

        selected_groups = form.cleaned_data.get("groups")
        if selected_groups:
            user.groups.set(selected_groups)

        messages.success(request, f"User '{user.username}' was created successfully.")
        return redirect("assets:user_list")

    return render(
        request,
        "users/user_form.html",
        {
            "form": form,
            "title": "Create User",
            "is_admin_editing": True,
            "can_manage_groups": True,
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
            edited_user = form.save(commit=False)
            edited_user.save()
            if can_manage_groups:
                form.save_m2m()
            messages.success(request, f"User '{edited_user.username}' was updated successfully.")
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
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' was deleted successfully.")
        return redirect("assets:user_list")

    return render(
        request,
        "users/user_confirm_delete.html",
        {"user": user}
    )


class IndexView(TemplateView):
    template_name = "assets/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        checked_out = AssetRequestItem.objects.filter(
            request__status=AssetRequest.APPROVED
        ).aggregate(
            total=Sum('approved_quantity')
        )['total'] or 0

        low_stock_items = Asset.objects.filter(
            Q(asset_type=Asset.CONSUMABLE, quantity__lte=10) |
            Q(asset_type=Asset.EQUIPMENT, quantity__lte=3)
        )

        context['total_assets']     = Asset.objects.count()
        context['available_assets'] = Asset.objects.filter(status="Available").count()
        context['checked_out']      = checked_out
        context['low_stock']        = low_stock_items.count()
        context['low_stock_items']  = low_stock_items
        return context

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
@permission_required("assets.delete_asset", raise_exception=True)
def asset_delete(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    if request.method == "POST":
        try:
            asset.delete()
            messages.success(request, f"Asset '{asset.name}' deleted successfully.")
        except ProtectedError:
            messages.error(
                request,
                f"Cannot delete '{asset.name}' because it is referenced in one or more requests. "
                "Remove or decline those requests first before deleting this asset."
            )
        return redirect("assets:asset_list")
    return render(request, "assets/delete_asset.html", {"asset": asset})


@login_required
@permission_required("assets.view_assetrequest", raise_exception=True)
def request_list(request):
    can_view_pending = request.user.has_perm("assets.view_pending_requests")
    can_view_history = request.user.has_perm("assets.view_request_history")
    can_approve      = request.user.has_perm("assets.approve_request")

    if can_view_pending:
        pending_qs = AssetRequest.objects.filter(status=AssetRequest.FOR_APPROVAL)
        if not can_approve:
            pending_qs = pending_qs.filter(created_by=request.user)
        pending = pending_qs.prefetch_related('items__asset').order_by('-created_at')
    else:
        pending = AssetRequest.objects.none()

    if can_view_history:
        history_qs = AssetRequest.objects.all() if can_approve else AssetRequest.objects.filter(created_by=request.user)
        history = history_qs.prefetch_related('items__asset').order_by('-created_at')
    else:
        history = AssetRequest.objects.none()

    context = {
        'requests':         pending,
        'history':          history,
        'can_view_pending': can_view_pending,
        'can_view_history': can_view_history,
        'can_approve':      can_approve,
    }
    return render(request, 'assets/request_list.html', context)


@login_required
@permission_required("assets.request_asset", raise_exception=True)
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
@permission_required("assets.approve_request", raise_exception=True)
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

            AssetLog.objects.create(
                asset=asset,
                action=AssetLog.ACTION_DEDUCTED,
                performed_by=request.user,
                notes=(
                    f"Deducted {decrement} unit(s) for Request #{ar.id}"
                    f" by {ar.requestor_name}"
                    + (f" ({ar.requestor_group})" if ar.requestor_group else "")
                    + f". Remaining stock: {asset.quantity}."
                ),
            )

        ar.status = AssetRequest.APPROVED
        ar.save()

    messages.success(request, "Request approved and inventory updated.")
    return redirect('assets:request_list')


@login_required
@permission_required("assets.approve_request", raise_exception=True)
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

@login_required
@permission_required("assets.view_asset", raise_exception=True)
def dashboard(request):
    """Overview of the inventory health, value, and request activity."""

    # Per-type "low stock" thresholds (at or below this, but above zero).
    EQUIPMENT_LOW_THRESHOLD = 3
    CONSUMABLE_LOW_THRESHOLD = 10

    # cost * quantity, evaluated in the database for the value rollups.
    value_expr = ExpressionWrapper(
        F("cost") * F("quantity"),
        output_field=DecimalField(max_digits=18, decimal_places=2),
    )

    assets = Asset.objects.all()

    totals = assets.aggregate(
        total_assets=Count("id"),
        total_units=Sum("quantity"),
        total_value=Sum(value_expr),
    )
    total_assets = totals["total_assets"] or 0
    total_units = totals["total_units"] or 0
    total_value = totals["total_value"] or Decimal("0")

    # Low stock uses a different threshold per asset type.
    low_stock_q = (
        Q(asset_type=Asset.EQUIPMENT, quantity__gt=0, quantity__lte=EQUIPMENT_LOW_THRESHOLD)
        | Q(asset_type=Asset.CONSUMABLE, quantity__gt=0, quantity__lte=CONSUMABLE_LOW_THRESHOLD)
    )
    low_stock_items = assets.filter(low_stock_q).order_by("quantity", "name")
    out_of_stock_items = assets.filter(quantity=0).order_by("name")
    low_stock_count = low_stock_items.count()
    out_of_stock_count = out_of_stock_items.count()

    # Per-type statistics (Equipment vs Consumable).
    def type_stats(type_qs, threshold):
        agg = type_qs.aggregate(count=Count("id"), value=Sum(value_expr))
        value = agg["value"] or Decimal("0")
        low = type_qs.filter(quantity__gt=0, quantity__lte=threshold).count()
        out = type_qs.filter(quantity=0).count()
        return {
            "count": agg["count"] or 0,
            "value": value,
            "value_display": f"{value:,.2f}",
            "low_stock": low,
            "out_of_stock": out,
            "attention": low + out,
            "threshold": threshold,
        }

    equipment_stats = type_stats(
        assets.filter(asset_type=Asset.EQUIPMENT), EQUIPMENT_LOW_THRESHOLD
    )
    consumable_stats = type_stats(
        assets.filter(asset_type=Asset.CONSUMABLE), CONSUMABLE_LOW_THRESHOLD
    )
    equipment_count = equipment_stats["count"]
    consumable_count = consumable_stats["count"]

    # Units issued out per asset (approved request items) = "usage".
    usage_rows = (
        AssetRequestItem.objects
        .filter(request__status=AssetRequest.APPROVED)
        .values("asset_id")
        .annotate(used=Sum("approved_quantity"))
    )
    usage_by_asset = {r["asset_id"]: int(r["used"] or 0) for r in usage_rows}

    # Usage vs. current stock for every low-stock item (drives the filterable graph).
    low_stock_usage = [
        {
            "id": a.id,
            "name": a.name,
            "type": a.get_asset_type_display(),
            "usage": usage_by_asset.get(a.id, 0),
            "stock": a.quantity,
        }
        for a in low_stock_items
    ]

    # Requests
    requests_qs = AssetRequest.objects.all()
    pending_count = requests_qs.filter(status=AssetRequest.FOR_APPROVAL).count()
    approved_count = requests_qs.filter(status=AssetRequest.APPROVED).count()
    declined_count = requests_qs.filter(status=AssetRequest.DECLINED).count()
    total_requests = requests_qs.count()

    recent_requests = (
        requests_qs.prefetch_related("items__asset").order_by("-created_at")[:5]
    )
    recent_logs = (
        AssetLog.objects.select_related("asset", "performed_by")
        .order_by("-timestamp")[:8]
    )

    # Inventory grouped by category (used for both the chart and the table)
    category_rows = (
        assets.values("category")
        .annotate(count=Count("id"), units=Sum("quantity"), value=Sum(value_expr))
        .order_by("-value")
    )
    category_table = [
        {
            "category": row["category"] or "Uncategorized",
            "count": row["count"],
            "units": row["units"] or 0,
            "value": row["value"] or Decimal("0"),
            "value_display": f"{(row['value'] or 0):,.2f}",
        }
        for row in category_rows
    ]

    # JSON-safe payload for the Chart.js visualizations
    chart_data = {
        "category": {
            "labels": [c["category"] for c in category_table],
            "values": [float(c["value"]) for c in category_table],
        },
        "type_value": {
            "labels": ["Equipment", "Consumable"],
            "values": [
                float(equipment_stats["value"]),
                float(consumable_stats["value"]),
            ],
        },
        "requests": {
            "labels": ["For Approval", "Approved", "Declined"],
            "counts": [pending_count, approved_count, declined_count],
        },
        "low_stock_usage": low_stock_usage,
    }

    context = {
        "total_assets": total_assets,
        "total_units": total_units,
        "total_units_display": f"{total_units:,}",
        "total_value": total_value,
        "total_value_display": f"{total_value:,.2f}",
        "equipment_count": equipment_count,
        "consumable_count": consumable_count,
        "equipment_stats": equipment_stats,
        "consumable_stats": consumable_stats,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "declined_count": declined_count,
        "total_requests": total_requests,
        "recent_requests": recent_requests,
        "recent_logs": recent_logs,
        "category_table": category_table,
        "equipment_low_threshold": EQUIPMENT_LOW_THRESHOLD,
        "consumable_low_threshold": CONSUMABLE_LOW_THRESHOLD,
        "low_stock_usage": low_stock_usage,
        "chart_data": chart_data,
    }
    return render(request, "assets/dashboard.html", context)

