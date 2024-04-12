from django.urls import path
from . import views
from .views import ContactFormView
from users.views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, custom_password_reset_complete
from django.conf import settings
from django.conf.urls.static import static
#from users.views import update_information, update_password, update_user, login_customer, logout_customer, user_signup

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_customer, name='logout'),
    path('update_password', views.update_password, name='update_password'),
    path('update_user/', views.update_user, name='update_user'),
    path('update_info/', views.update_information, name='update_info'),
    path('product/<int:pk>', views.product, name='product'),
    path('category/<str:bar>', views.category, name='category'),
    path('category_summary', views.category_summary, name='category_summary'),
    path('register', views.user_signup, name='register'),
    path('search/', views.search_product, name='search'),
    path('contact', ContactFormView.as_view(), name='contact'),
    path('about/', views.about, name='about'),
    path('login/', views.login_customer, name='login'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', custom_password_reset_complete, name='password_reset_complete'),
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)