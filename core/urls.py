from django.contrib import admin
from django.urls import path, include
from apps_gestao import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('register/', views.register, name='register'),
    path('novo-pedido/', views.novo_pedido, name='novo_pedido'),
    
    # ROTAS QUE ESTÃO A FALTAR E CAUSAM O ERRO:
    path('aprovar/<int:pedido_id>/', views.aprovar_pedido, name='aprovar_pedido'),
    path('recusar/<int:pedido_id>/', views.recusar_pedido, name='recusar_pedido'),
    
    path('ativar-utilizador/<int:user_pk>/', views.ativar_utilizador, name='ativar_utilizador'),
    
    # Rotas do Mapa e Turnos (garante que também aqui estão)
    path('mapa/', views.mapa_ferias, name='mapa_ferias'),
    path('atribuir-turno/', views.atribuir_turno, name='atribuir_turno'),
    
    path('', views.dashboard, name='dashboard'),
]