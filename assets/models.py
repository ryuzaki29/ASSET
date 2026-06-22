from django.db import models
from django.contrib.auth.models import User

# Updated Profile model
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.user.username
    
class Asset(models.Model):
    EQUIPMENT = "equipment"
    CONSUMABLE = "consumable"
    TYPE_CHOICES = [
        (EQUIPMENT, "Equipment"),
        (CONSUMABLE, "Consumable"),
    ]

    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.CharField(max_length=50)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=50)
    log_details = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"
        
        permissions = [
            ("audit_assets", "Can Audit Assets"),
            ("request_asset", "Can Request Asset"),
            ("approve_request", "Can Approve Request"),
        ]


class AssetRequest(models.Model):
    FOR_APPROVAL = "For Approval"
    APPROVED = "Approved"
    DECLINED = "Declined"
    STATUS_CHOICES = [
        (FOR_APPROVAL, "For Approval"),
        (APPROVED, "Approved"),
        (DECLINED, "Declined"),
    ]

    requestor_name = models.CharField(max_length=200)
    requestor_group = models.CharField(max_length=200, blank=True)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=FOR_APPROVAL)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    decline_reason = models.TextField(blank=True, default="")

    def has_sufficient_stock(self):
        return all(it.asset.quantity >= it.quantity for it in self.items.all())

    def has_earlier_pending_conflicts(self):
        my_asset_ids = set(self.items.values_list('asset_id', flat=True))
        if not my_asset_ids:
            return False
        return (
            AssetRequest.objects
            .filter(
                status=AssetRequest.FOR_APPROVAL,
                created_at__lt=self.created_at,
                items__asset_id__in=my_asset_ids
            )
            .exclude(id=self.id)
            .exists()
        )

    def __str__(self):
        return f"Request #{self.id} by {self.requestor_name}"

    class Meta:
        permissions = [
            ("view_pending_requests", "Can View Pending Request Table"),
            ("view_request_history", "Can View Request History Table"),
        ]


class AssetLog(models.Model):
    ACTION_CREATED = "Created"
    ACTION_EDITED  = "Edited"
    ACTION_STOCK   = "Stock Added"

    asset         = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='logs')
    action        = models.CharField(max_length=50)
    performed_by  = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes         = models.TextField(blank=True)
    timestamp     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} — {self.asset.name}"


class AssetRequestItem(models.Model):
    request = models.ForeignKey(AssetRequest, related_name="items", on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    approved_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.quantity} x {self.asset.name} for request #{self.request.id}"
