from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"bookings", views.BookingViewSet, basename="booking")

urlpatterns = [
    path("menu/", views.MenuItemsView.as_view(), name="menu-list"),
    path("menu/<int:pk>/", views.SingleMenuItemView.as_view(), name="menu-detail"),
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path("token/login/", obtain_auth_token, name="token-login"),
    path("", include(router.urls)),
]
