from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    max_failed_attempts = 5
    lockout_time = 15  # Lockout duration in minutes

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        
        # Automatically unlock if lockout period has passed
        self.auto_unlock_account(user)
        
        # Reset failed attempts on successful login
        self.reset_failed_attempts(user)
        logger.info(f"User {user.username} logged in successfully.")

        # Role-based redirection
        if user.is_superuser:
            self.success_url = reverse_lazy('admin_dashboard')
        elif user.is_staff:
            self.success_url = reverse_lazy('staff_dashboard')
        else:
            self.success_url = reverse_lazy('user_dashboard')

        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle failed login attempts."""
        request = self.request
        username = form.cleaned_data.get('username')

        if username:
            user = authenticate(username=username, password=form.cleaned_data.get('password'))
            if user:
                self.track_failed_attempts(user)
            else:
                logger.warning(f"Failed login attempt for username: {username} from IP: {self.get_client_ip()}")

        messages.error(request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

    def track_failed_attempts(self, user):
        """Track and lock the account if max failed attempts are reached."""
        current_time = datetime.now()
        time_since_last_attempt = current_time - user.last_failed_login if user.last_failed_login else None
        
        # Automatically unlock if lockout period has passed
        if time_since_last_attempt and time_since_last_attempt > timedelta(minutes=self.lockout_time):
            self.reset_failed_attempts(user)
            return

        # Lock account if max failed attempts reached
        if user.failed_attempts >= self.max_failed_attempts:
            user.is_active = False
            user.save()
            self.send_lockout_email(user)
            messages.error(self.request, "Your account is locked due to multiple failed login attempts. Please try again later.")
            logger.warning(f"Account for {user.username} locked due to failed login attempts from IP: {self.get_client_ip()}.")
            return

        # Increment failed attempts count and update timestamp
        user.failed_attempts += 1
        user.last_failed_login = current_time
        user.save()

    def reset_failed_attempts(self, user):
        """Reset failed login attempts after a successful login."""
        user.failed_attempts = 0
        user.last_failed_login = None
        user.is_active = True
        user.save()

    def auto_unlock_account(self, user):
        """Automatically unlocks account if the lockout time has passed."""
        if not user.is_active and user.failed_attempts >= self.max_failed_attempts:
            time_since_lockout = datetime.now() - user.last_failed_login
            if time_since_lockout > timedelta(minutes=self.lockout_time):
                self.reset_failed_attempts(user)
                logger.info(f"Account for {user.username} automatically unlocked after lockout period.")

    def send_lockout_email(self, user):
        """Send an email to the user when their account is locked."""
        if user.email:
            send_mail(
                subject="Account Locked Due to Failed Login Attempts",
                message=f"Dear {user.username}, your account has been locked due to multiple failed login attempts. "
                        "Please wait for the lockout period to pass or contact support if you require further assistance.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email]
            )
            logger.info(f"Lockout notification email sent to {user.email}")

    def get_client_ip(self):
        """Retrieve the client's IP address."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def dispatch(self, *args, **kwargs):
        logger.info(f"User {self.request.user.username} logged out.")
        messages.info(self.request, "You have successfully logged out.")
        return super().dispatch(*args, **kwargs)
