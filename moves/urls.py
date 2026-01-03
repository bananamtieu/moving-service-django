# moves/urls.py
from django.urls import path
from . import views

app_name = 'moves'

urlpatterns = [
    path('', views.MoveListView.as_view(), name='list'),
    path('driver/', views.DriverMoveListView.as_view(), name='driver_list'),
    path('staff/', views.StaffMoveListView.as_view(), name='staff_list'),
    path('new/', views.MoveCreateView.as_view(), name='create'),
    path('<int:pk>/', views.MoveDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.MoveUpdateView.as_view(), name='update'),
    path('<int:pk>/cancel/', views.MoveCancelView.as_view(), name='cancel'),
    path('<int:pk>/assign-driver/', views.StaffAssignDriverView.as_view(), name='assign_driver'),
]
