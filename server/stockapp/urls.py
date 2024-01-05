from django.urls import path
from . import views

urlpatterns = [
    path('api/stocks/', views.stock_api, name='stock_api'),
]