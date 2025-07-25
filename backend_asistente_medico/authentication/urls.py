from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/check-auth/', views.check_auth, name='check_auth'),
    # path('auth/protected/', views.protected_view, name='protected'),
    path('auth/register/', views.register_view, name='register'),
]