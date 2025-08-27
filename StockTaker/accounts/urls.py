from django.urls import path, include, reverse, re_path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.register, name='signup'),

    # Google login redirect - when user clicks the Google login button
    path('google-login/', views.GoogleLoginRedirectApi.as_view(), name='google-login'),

    # Google login callback - after user authenticates with Google
    path('google-login/callback/', views.GoogleLoginApi.as_view(),
         name='google_login_callback'),

    # path('user', views.UserDetailView.as_view(), name='user-detail'),
    path('user/<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
    re_path(r'^user/(?P<pk>\d+)/update/$',
            views.UserUpdateView.as_view(), name='user-update'),
    re_path(r'^profile/(?P<pk>\d+)/update/$',
            views.ProfileUpdateView.as_view(), name='profile-update'),
]
