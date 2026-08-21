# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), # Root path points to the home view
]