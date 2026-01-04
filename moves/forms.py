# moves/forms.py
from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import MoveRequest

User = get_user_model()

class MoveRequestForm(forms.ModelForm):
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
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
        date = self.cleaned_data['scheduled_date']
        if date <= timezone.localdate():
            raise forms.ValidationError('Please choose a future date.')
        return date

class StaffAssignDriverForm(forms.ModelForm):
    class Meta:
        model = MoveRequest
        fields = ['driver']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['driver'].queryset = (
            User.objects
            .filter(role='driver')
            .order_by('username')
        )
        self.fields['driver'].required = True
    
    def clean_driver(self):
        driver = self.cleaned_data['driver']
        if getattr(driver, 'role', None) != 'driver':
            raise forms.ValidationError('Selected user is not a driver.')
        return driver

class DriverStatusForm(forms.ModelForm):
    class Meta:
        model = MoveRequest
        fields = ['status']
    
    def clean_status(self):
        status = self.cleaned_data['status']
        allowed = {'accepted', 'in_progress', 'completed'}
        if status not in allowed:
            raise forms.ValidationError('Invalid status update.')
        return status
