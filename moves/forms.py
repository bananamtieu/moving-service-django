# moves/forms.py
from django import forms
from django.utils import timezone
from .models import MoveRequest

class MoveRequestForm(forms.ModelForm):
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
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
        date = self.cleaned_data["scheduled_date"]
        if date <= timezone.localdate():
            raise forms.ValidationError("Please choose a future date.")
        return date

class StaffAssignForm(forms.ModelForm):
    class Meta:
        model = MoveRequest
        fields = ['driver', 'status', 'estimated_price']
