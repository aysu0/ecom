from django.urls import path
from . import views

urlpatterns = [
    path('', views.shoppingcart_summary, name="cart_summary"),
    path('add/', views.shoppingcart_add, name="cart_add"),
    path('delete/', views.shoppingcart_delete, name="cart_delete"),
    path('update/', views.shoppingcart_update, name="cart_update"),

]
