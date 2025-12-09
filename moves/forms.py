# moves/forms.py
from django import forms
from .models import MoveRequest

class MoveRequestForm(forms.ModelForm):
    scheduled_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
    )

    class Meta:
        model = MoveRequest
        # Fields the CUSTOMER can edit directly
        fields = [
            'pickup_address',
            'dropoff_address',
            'scheduled_date',
            'notes',
        ]
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_scheduled_date(self):
        from django.utils import timezone
        dt = self.cleaned_data['scheduled_date']
        if dt <= timezone.now():
            raise forms.ValidationError("Please choose a time in the future.")
        return dt
