from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

# Import Asset Model for Permission Filtering
from assets.models import Asset 

User = get_user_model()

class CleanPermissionChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        name = obj.name
        if name.lower().startswith("can "):
            name = name[4:]
        name = name.replace("change", "edit")
        return name.title()


class GroupForm(forms.ModelForm):
    permissions = CleanPermissionChoiceField(
        queryset=Permission.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Automatically fetch the correct content types
        user_ct = ContentType.objects.get_for_model(User)
        asset_ct = ContentType.objects.get_for_model(Asset)
        
        # Filter using the verified content types
        self.fields["permissions"].queryset = Permission.objects.filter(
            content_type__in=[user_ct, asset_ct]
        ).order_by("content_type__model", "codename")

    def get_grouped_permissions(self):
        """
        Splits the field's checkboxes into organized section buckets 
        for semantic rendering in the template layout.
        """
        user_ct = ContentType.objects.get_for_model(User)
        asset_ct = ContentType.objects.get_for_model(Asset)
        
        # Pull sets of IDs belonging to each content type to cross-reference
        user_ids = set(Permission.objects.filter(content_type=user_ct).values_list('id', flat=True))
        asset_ids = set(Permission.objects.filter(content_type=asset_ct).values_list('id', flat=True))
        
        user_widgets = []
        asset_widgets = []
        
        # Cycle through checkboxes, matching permission IDs to their respective category
        for widget in self['permissions']:
            try:
                val_id = int(str(widget.data['value']))
            except (ValueError, TypeError):
                continue
                
            if val_id in user_ids:
                user_widgets.append(widget)
            elif val_id in asset_ids:
                asset_widgets.append(widget)
                
        return {
            'User Management': user_widgets,
            'Asset Management': asset_widgets,
        }