from django.urls import path, include
from . import views

urlpatterns = [
    path('payment_success', views.payment_success, name='payment_success'),
    path('checkout', views.checkout, name='checkout'),
    path('user_billing_information', views.user_billing_information, name="user_billing_information"),
    path('payment-session', views.createStripePayment, name="payment-session"),
    path('handle_order', views.handle_order, name="handle_order"),
    path('payment_failed', views.payment_failed, name='payment_failed'),

]