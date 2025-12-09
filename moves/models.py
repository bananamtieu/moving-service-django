from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

# Create your models here.
class MoveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_moves')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_moves')

    pickup_address = models.CharField(max_length=255)
    dropoff_address = models.CharField(max_length=255)
    scheduled_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    notes = models.TextField(blank=True)
    estimated_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MoveRequest {self.id} for {self.customer.username}"