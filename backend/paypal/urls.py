from django.urls import path
from . import views

urlpatterns = [

    # paypal
    path('orders/', views.create_order, name="create_order"),
    path('orders/capture/', views.capture_order, name='capture_order'),
    
    # user
    path('purchases/', views.purchases, name="purchases"),


]

