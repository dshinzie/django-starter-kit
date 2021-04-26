from django.urls import path
from . import views

urlpatterns = [
    # profile
    path('info/', views.UserInfoView.as_view(), name='user_info'),
    path('sample/', views.SampleTemplateView.as_view(), name='sample'),
]