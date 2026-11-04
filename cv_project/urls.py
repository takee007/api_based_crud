from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('cv_app.urls')),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('login.html', TemplateView.as_view(template_name='login.html'), name='login-html'),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]
