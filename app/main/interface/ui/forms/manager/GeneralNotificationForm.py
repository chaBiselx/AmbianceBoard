from django import forms
from main.architecture.persistence.models.GeneralNotification import GeneralNotification
from main.domain.common.mixins.BootstrapFormMixin import BootstrapFormMixin
from django.utils import timezone


class GeneralNotificationForm(BootstrapFormMixin, forms.ModelForm):
    """
    Formulaire pour créer et modifier les notifications générales.
    """
    
    class Meta:
        model = GeneralNotification
        fields = (
            'message',
            'class_name',
            'start_date',
            'end_date',
            'for_authenticated_users',
            'is_active',
        )
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Contenu HTML de la notification'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
            }),
            'end_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['message'].widget.attrs['class'] = self.fields['message'].widget.attrs.get('class', '') + ' editor-container'
        self.fields['message'].widget.attrs['data-editor'] = 'simple'
        
        # Valeurs par défaut pour une nouvelle notification
        if not self.instance.pk:
            self.fields['start_date'].initial = timezone.now()
            self.fields['is_active'].initial = True
            
        # Formater les dates pour datetime-local input
        if self.instance.pk:
            if self.instance.start_date:
                self.initial['start_date'] = self.instance.start_date.strftime('%Y-%m-%dT%H:%M')
            if self.instance.end_date:
                self.initial['end_date'] = self.instance.end_date.strftime('%Y-%m-%dT%H:%M')
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError(
                    'La date de fin doit être postérieure à la date de début.'
                )
        
        return cleaned_data
