from django import forms
from main.architecture.persistence.models.PlaylistTag import PlaylistTag
from main.domain.common.mixins.BootstrapFormMixin import BootstrapFormMixin


class PlaylistTagForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PlaylistTag
        fields = ("name", "description", "is_active")

    name = forms.CharField(
        label="Nom du tag playlist",
        max_length=50,
        required=True,
        help_text="Nom du tag playlist (3-50 caracteres)",
    )

    description = forms.CharField(
        label="Description",
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Description optionnelle du tag playlist",
    )

    is_active = forms.BooleanField(
        required=False,
        label="Tag actif",
        initial=True,
        help_text="Indique si le tag playlist est actif et utilisable",
    )
