from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'
    login_url = 'login'  # Redirect unauthenticated users to the login page

class StaffDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/staff_dashboard.html'
    login_url = 'login'  # Redirect unauthenticated users to the login page

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/admin_dashboard.html'
    login_url = 'login'  # Redirect unauthenticated users to the login page
