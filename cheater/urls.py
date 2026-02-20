"""
URL configuration for cheater project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ciscoapp.views import buscar, activate, verify_activation, home, consultar_gemini, consultar_gemini_imagen

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path('buscar/', buscar, name='buscar'),
    path('activate/', activate, name='activate'),
    path('verify_activation/', verify_activation, name='verify_activation'),
    path('consultar_gemini/', consultar_gemini, name='consultar_gemini'),
    path('consultar_gemini_imagen/', consultar_gemini_imagen, name='consultar_gemini_imagen'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
