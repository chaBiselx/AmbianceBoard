from django import forms
from main.architecture.persistence.models.HomeDemoItem import HomeDemoItem
from main.domain.common.mixins.BootstrapFormMixin import BootstrapFormMixin


class HomeDemoItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = HomeDemoItem
        fields = (
            'title',
            'icon',
            'state_text',
            'aria_label',
            'is_active',
        )

    def __init__(self, *args, **kwargs):
        self.selected_soundboard = kwargs.pop('selected_soundboard', None)
        super().__init__(*args, **kwargs)
        if self.selected_soundboard is not None and self.instance.pk is None:
            self.instance.soundboard = self.selected_soundboard
        self.fields['title'].widget.attrs.update({
            'placeholder': 'Ex: Medieval',
        })
        self.fields['icon'].widget.attrs.update({
            'placeholder': 'Ex: ⚔️',
            'maxlength': 8,
        })
        self.fields['state_text'].widget.attrs.update({
            'placeholder': 'Ex: Cliquer pour jouer',
        })
        self.fields['aria_label'].widget.attrs.update({
            'placeholder': "Optionnel: Jouer l'ambiance Medieval",
        })

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk is None:
            if self.selected_soundboard is None:
                raise forms.ValidationError('Veuillez sélectionner un soundboard public avant de créer la démo.')
            instance.soundboard = self.selected_soundboard
        if commit:
            instance.save()
            self.save_m2m()
        return instance
