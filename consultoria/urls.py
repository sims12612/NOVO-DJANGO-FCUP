from django.urls import path
from . import views
from .views import user_login, user_logout, client_dashboard, consultant_dashboard, dashboard, criar_pedido,meus_servicos_pedidos
from .views import marcar_concluido

urlpatterns = [
    path('', views.welcome, name='welcome'),  # Página inicial
    path('lista/', views.lista_consultores, name='lista_consultores'),  # Página com lista de consultores
    path('reservar/', views.reservar_consultor, name='reservar_consultor'),  # Página de reserva
    path('registrar/', views.registrar_consultor, name='registrar_consultor'),  # Página de registr
    path('registar_cliente/', views.criar_pedido, name='criar_pedido'),
    path('sucesso/<str:nome>/<str:categoria>/<str:especialidade>/<str:morada>/<str:descricao>/<str:telemovel>/', views.pedidoregistadocomsucesso, name='pedidoregistadocomsucesso'),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("client/dashboard/", client_dashboard, name="client_dashboard"),
    path("consultant/dashboard/", consultant_dashboard, name="consultant_dashboard"),
    path('registar_user/', views.registar_user, name='registar_user'),
    path('criar_pedido/', views.criar_pedido, name='criar_pedido'),
    path('dashboard/', views.dashboard, name='dashboard'),  # URL da Dashboard
    path('escolher_categoria/', views.escolher_categoria, name='escolher_categoria'),
    path('pagar_pedido/<int:preco>/<int:num_pedidos>/<str:categoria>/', views.pagar_pedido, name='pagar_pedido'),
    path('ultimos_pedidos/<int:pedido_id>/', views.ultimos_pedidos, name='ultimos_pedidos'),
    path('processar_pagamento/<int:preco>/<int:num_pedidos>/<str:categoria>/', views.processar_pagamento, name='processar_pagamento'),
    path('pagamento/sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('pagamento/cancelado/', views.pagamento_cancelado, name='pagamento_cancelado'),
    path('meus_servicos_pedidos/', views.meus_servicos_pedidos, name='meus_servicos_pedidos'),
    path('pedidos_visualizacao_servicos/', views.pedidos_visualizacao_servicos, name='pedidos_visualizacao_servicos'),
    path('area_cliente/', views.area_cliente, name='area_cliente'),
    path('area_consultor/', views.area_consultor, name='area_consultor'),
    path("marcar_concluido/", views.marcar_concluido, name="marcar_concluido"),
]


