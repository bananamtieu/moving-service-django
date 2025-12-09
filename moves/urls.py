# moves/urls.py
from django.urls import path
from . import views

app_name = 'moves'

urlpatterns = [
    path('', views.move_list, name='list'),
    path('new/', views.move_create, name='create'),
    path('<int:pk>/', views.move_detail, name='detail'),
    path('<int:pk>/edit/', views.move_update, name='update'),
    path('<int:pk>/cancel/', views.move_cancel, name='cancel'),
]