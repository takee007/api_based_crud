from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentCVViewSet,
    StudentLoginView,
    StudentRegisterView,
    StudentMeView,
    StudentLogoutView
)

router = DefaultRouter()
router.register(r'cvs', StudentCVViewSet, basename='cv')

urlpatterns = [
    # Auth endpoints
    path('auth/login/', StudentLoginView.as_view(), name='student-login'),
    path('auth/register/', StudentRegisterView.as_view(), name='student-register'),
    path('auth/me/', StudentMeView.as_view(), name='student-me'),
    path('auth/logout/', StudentLogoutView.as_view(), name='student-logout'),

    # CV CRUD endpoints
    path('', include(router.urls)),
]
