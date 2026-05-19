from django.db import models
# Profile model import added (Joper)
from django.contrib.auth.models import User

class Profile(models.Model):
    DESIGNATION_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('UTILITY', 'Utility Staff'),
        ('ITDC', 'ITDC Staff'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=11)
    designation = models.CharField(max_length=20,
        choices=DESIGNATION_CHOICES)
    
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
