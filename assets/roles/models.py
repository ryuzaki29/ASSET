from django.db import models


class Role(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)