from django.urls import path
from .views import HomeView, StaffDashboardView, AdminDashboardView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # Home page (requires login)
    path('staff/', StaffDashboardView.as_view(), name='staff_dashboard'),  # Staff dashboard (requires login)
    path('admin/', AdminDashboardView.as_view(), name='admin_dashboard'),  # Admin dashboard (requires login)
]
