from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
import logging
from datetime import datetime, timedelta

# Initialize logger
logger = logging.getLogger(__name__)
User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('home')
    max_failed_attempts = 5
    lockout_time = 15  # in minutes

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        self.reset_failed_attempts(user)
        logger.info(f"User {user.username} logged in successfully.")

        # Redirect users based on their role
        if user.is_staff:
            self.success_url = reverse_lazy('staff_dashboard')
        elif user.is_superuser:
            self.success_url = reverse_lazy('admin_dashboard')
        else:
            self.success_url = reverse_lazy('user_dashboard')

        return super().form_valid(form)

    def form_invalid(self, form):
        request = self.request
        username = form.cleaned_data.get('username', '')

        if username:
            user = authenticate(username=username, password=form.cleaned_data.get('password'))
            if user:
                self.track_failed_attempts(user)
            else:
                logger.warning(f"Failed login attempt for {username}.")

        messages.error(request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

    def track_failed_attempts(self, user):
        if user.failed_attempts >= self.max_failed_attempts:
            if datetime.now() - user.last_failed_login < timedelta(minutes=self.lockout_time):
                user.is_active = False
                user.save()
                messages.error(self.request, "Your account is locked. Please try again later.")
                return

        user.failed_attempts += 1
        user.last_failed_login = datetime.now()
        user.save()

    def reset_failed_attempts(self, user):
        user.failed_attempts = 0
        user.is_active = True
        user.save()

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def dispatch(self, *args, **kwargs):
        logger.info(f"User {self.request.user.username} logged out.")
        messages.info(self.request, "You have successfully logged out.")
        return super().dispatch(*args, **kwargs)
