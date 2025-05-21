from django.urls import path
from . import views

app_name = 'maquinas'

urlpatterns = [
    path('layout/', views.exibir_layout_empresa, name='layout_empresa'),
    path('atualizar-posicao/', views.atualizar_posicao_maquina, name='atualizar_posicao_maquina'),
]