from django import forms
from home.models.Tag import Tag
from home.mixins.BootstrapFormMixin import BootstrapFormMixin


class TagForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name', 'description', 'is_active')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    name = forms.CharField(
        label='Nom du tag', 
        max_length=50, 
        required=True,
        help_text="Nom du tag (3-50 caractères)"
    )
    
    description = forms.CharField(
        label='Description',
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="Description optionnelle du tag"
    )
    
    is_active = forms.BooleanField(
        required=False, 
        label='Tag actif', 
        initial=True,
        help_text="Indique si le tag est actif et peut être utilisé"
    )
