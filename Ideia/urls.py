from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Acesso ao painel de administração do Django
    path('consultoria/', include('consultoria.urls')),  # Inclui as URLs da aplicação consultoria
    path('', include('consultoria.urls')),  # Redireciona a página inicial para a app consultoria
]
