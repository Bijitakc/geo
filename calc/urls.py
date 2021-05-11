from django.urls import path
from .views import calculate_distance_view

app_name='calc'

urlpatterns = [
    path('',calculate_distance_view,name='calculate'),
]