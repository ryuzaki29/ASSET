from django.db import models

class Role(models.Model):
    # Using choices to restrict it to Administrator, Executive, and Staff
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('EXEC', 'Executive'),
        ('STAFF', 'Staff'),
    ]
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name