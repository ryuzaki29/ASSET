from django.db import models
from django.contrib.auth.models import User
from assets.roles.models import Role

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    designation = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
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
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.id} by {self.requestor_name} [{self.status}]"


class AssetRequestItem(models.Model):
    request = models.ForeignKey(AssetRequest, on_delete=models.CASCADE, related_name='items')
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.asset.name} x{self.quantity} for Request #{self.request.id}"
