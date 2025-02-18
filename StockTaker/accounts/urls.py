from django.urls import path, include, reverse
from . import views


urlpatterns = [
    path('signup/',views.register,name='signup'),

    # Google login redirect - when user clicks the Google login button
    path('google-login/', views.GoogleLoginRedirectApi.as_view(), name='google-login'),
    
    # Google login callback - after user authenticates with Google
    path('google-login/callback/', views.GoogleLoginApi.as_view(), name='google_login_callback'),
]

