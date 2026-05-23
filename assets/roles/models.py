from django.db import models


class Role(models.Model):

    # internal role identifier (used in code/logic)
    name = models.CharField(
        max_length=20,
        unique=True             
    )

    # human-readable description (free text / flexible)
    description = models.CharField(
        max_length=255,
        blank=True
    )

    def __str__(self):
        return self.name            