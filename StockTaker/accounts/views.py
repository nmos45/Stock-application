from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from .forms import CreateUserForm
from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts import redirect
from .google_auth import GoogleRawLoginFlowService
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from rest_framework import serializers, status
from rest_framework.response import Response
from django.views.generic.detail import DetailView
from django.views.generic import UpdateView
import requests
from .forms import UserForm, ProfileForm
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import Profile
import requests


class GoogleLoginApi(View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        error = request.GET.get('error')
        state = request.GET.get('state')

        # Check for any errors in the callback
        if error is not None:
            return JsonResponse(
                {"error": error},
                status=400
            )

        if code is None or state is None:
            return JsonResponse(
                {"error": "Code and state are required."},
                status=400
            )

        session_state = request.session.get("google_oauth2_state")

        # CSRF protection - check if the state matches the one stored in the session
        if session_state is None:
            return JsonResponse(
                {"error": "CSRF check failed."},
                status=400
            )

        if session_state != state:
            return JsonResponse(
                {"error": " state CSRF check failed."},
                status=400
            )
        del request.session["google_oauth2_state"]

        # Exchange the authorization code for an access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            "redirect_uri": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI,
            "grant_type": "authorization_code"
        }

        token_response = requests.post(token_url, data=token_data)

        if token_response.status_code != 200:
            return JsonResponse(
                {"error": "Failed to obtain access token."},
                status=400
            )

        # Get the access token from the response
        token_json = token_response.json()
        access_token = token_json.get("access_token")

        # Use the access token to fetch user data from Google
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)

        if user_info_response.status_code != 200:
            return JsonResponse(
                {"error": "Failed to fetch user information."},
                status=400
            )

        user_info = user_info_response.json()
        email = user_info.get("email")
        first_name = user_info.get("given_name")
        last_name = user_info.get("family_name")
        # google_id = user_info.get("id")
        profile_picture = user_info.get("picture")

        # Check if the user exists already
        user = User.objects.filter(email=email).first()

        if not user:
            # Create a new user if they don't exist
            user = User.objects.create_user(
                username=email.split("@")[0],
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=None  # Google login does not require a password
            )
        else:
            user.username = email.split("@")[0]
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # Log the user in
        login(request, user)

        # Redirect to the home page or a custom dashboard after login
        return redirect(settings.SOCIAL_AUTH_LOGIN_REDIRECT_URL)


def register(request):
    form = CreateUserForm()  # covers get requests

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect(reverse('login'))

    context = {'form': form}

    return render(request, 'registration/signup.html', context=context)


class GoogleLoginRedirectApi(View):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)


class UserDetailView(DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'accounts/user_update.html'

    def get_success_url(self):
        return self.request.path


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile_update.html'

    def get_success_url(self):
        return reverse_lazy('accounts:user-detail', kwargs={'username': self.object.user.username})
