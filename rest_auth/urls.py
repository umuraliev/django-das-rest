from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register', views.RegisterView.as_view()),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('login', views.LoginView.as_view(), name='login'),
    path('activation', views.ActivationView.as_view()),
    path('users', views.UserListAPIView.as_view()),

]
