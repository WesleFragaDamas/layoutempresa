from django.urls import path
from . import views # Importa o módulo views para as function-based views
from .views import ( # Importa as Class-Based Views especificamente
    PlantaLayoutListView,
    PlantaLayoutCreateView,
    PlantaLayoutUpdateView,
    PlantaLayoutDeleteView,
    MaquinaFisicaListView, # Certifique-se que estes estão sendo importados
    MaquinaFisicaCreateView,
    MaquinaFisicaUpdateView,
    MaquinaFisicaDeleteView,
)

app_name = 'maquinas'

urlpatterns = [
    # URLs do Layout Visual
    path('layout/', views.exibir_layout_empresa, name='layout_empresa_padrao'),
    path('layout/<int:planta_id>/', views.exibir_layout_empresa, name='layout_empresa_especifica'),
    path('atualizar-posicao/', views.atualizar_posicao_maquina, name='atualizar_posicao_maquina'),

    # URLs CRUD de PlantaLayout
    path('plantas/', PlantaLayoutListView.as_view(), name='plantalayout_list'),
    path('plantas/adicionar/', PlantaLayoutCreateView.as_view(), name='plantalayout_add'),
    path('plantas/<int:pk>/editar/', PlantaLayoutUpdateView.as_view(), name='plantalayout_edit'),
    path('plantas/<int:pk>/excluir/', PlantaLayoutDeleteView.as_view(), name='plantalayout_delete'),

    # URLs CRUD de MaquinaFisica
    path('maquinas/', MaquinaFisicaListView.as_view(), name='maquinafisica_list'),
    path('maquinas/adicionar/', MaquinaFisicaCreateView.as_view(), name='maquinafisica_add'),
    path('maquinas/<int:pk>/editar/', MaquinaFisicaUpdateView.as_view(), name='maquinafisica_edit'),
    path('maquinas/<int:pk>/excluir/', MaquinaFisicaDeleteView.as_view(), name='maquinafisica_delete'),

    # URLs Criar chamados
    path('chamado/criar/', views.criar_chamado_ajax, name='chamado_criar'),

]