from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models import Q

from assets.models import Asset, AssetRequest

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

        user_ct = ContentType.objects.get_for_model(User)
        asset_ct = ContentType.objects.get_for_model(Asset)
        asset_request_ct = ContentType.objects.get_for_model(AssetRequest)
        group_ct = ContentType.objects.get_for_model(Group)

        self.fields["permissions"].queryset = Permission.objects.filter(
            Q(content_type=asset_ct) |
            Q(content_type=asset_request_ct, codename__in=[
                "view_assetrequest", "view_pending_requests", "view_request_history"
            ]) |
            Q(content_type=user_ct) |
            Q(content_type=group_ct)
        ).order_by("content_type__model", "codename")

    def get_grouped_permissions(self):
        user_ct = ContentType.objects.get_for_model(User)
        asset_ct = ContentType.objects.get_for_model(Asset)
        asset_request_ct = ContentType.objects.get_for_model(AssetRequest)
        group_ct = ContentType.objects.get_for_model(Group)

        # approve_request is defined on Asset model but belongs under Request Management
        asset_ids = set(
            Permission.objects.filter(content_type=asset_ct)
            .exclude(codename='approve_request')
            .values_list('id', flat=True)
        )
        request_ids = set(
            Permission.objects.filter(
                Q(content_type=asset_request_ct) |
                Q(content_type=asset_ct, codename='approve_request')
            ).values_list('id', flat=True)
        )
        user_ids = set(Permission.objects.filter(content_type=user_ct).values_list('id', flat=True))
        group_ids = set(Permission.objects.filter(content_type=group_ct).values_list('id', flat=True))

        asset_widgets = []
        request_widgets = []
        user_widgets = []
        role_widgets = []

        for widget in self['permissions']:
            try:
                val_id = int(str(widget.data['value']))
            except (ValueError, TypeError):
                continue

            if val_id in asset_ids:
                asset_widgets.append(widget)
            elif val_id in request_ids:
                request_widgets.append(widget)
            elif val_id in user_ids:
                user_widgets.append(widget)
            elif val_id in group_ids:
                role_widgets.append(widget)

        return {
            'Asset Management': asset_widgets,
            'Request Management': request_widgets,
            'User Management': user_widgets,
            'Role Management': role_widgets,
        }
