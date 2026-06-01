from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm


from .models import Asset


admin.site.site_header = "Asset Management"
admin.site.site_title = "Asset Management"
admin.site.index_title = "Asset Management"

admin.site.register(Asset)