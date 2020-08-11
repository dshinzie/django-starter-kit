from django.urls import path
from . import views

urlpatterns = [
    path('registration/', views.CustomRegisterView.as_view(), name='registration'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('forgot-password/', views.CustomPasswordResetView.as_view(), name='forgot_password'),
    path('reset-password/', views.CustomPasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    path('update-password/', views.CustomPasswordChangeView.as_view(), name='update_password'),
]
