# maquinas/filters.py
import django_filters
from .models import PlantaLayout, MaquinaFisica, Chamado # Adicionado Chamado
from django.contrib.auth import get_user_model # Para filtrar por usuário

User = get_user_model()


class PlantaLayoutFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains', label='Nome da Planta')
    # Você pode adicionar mais filtros aqui, por exemplo, para descrição
    # descricao = django_filters.CharFilter(lookup_expr='icontains', label='Descrição Contém')

    class Meta:
        model = PlantaLayout
        fields = ['nome'] # Campos que aparecerão diretamente no formulário do filtro
                         # Se você definir filtros nomeados acima, não precisa listá-los aqui
                         # a menos que queira que eles sejam renderizados automaticamente de forma simples.
                         # Para campos de CharFilter como 'nome', é bom defini-los explicitamente para usar 'icontains'.

class MaquinaFisicaFilter(django_filters.FilterSet):
    nome_patrimonio = django_filters.CharFilter(lookup_expr='icontains', label='Nome/Patrimônio')
    setor = django_filters.CharFilter(lookup_expr='icontains', label='Setor')
    tipo_equipamento = django_filters.CharFilter(lookup_expr='icontains', label='Tipo de Equipamento')
    # Filtrar por ForeignKey (PlantaLayout)
    # Isso criará um dropdown com as plantas existentes
    planta_layout = django_filters.ModelChoiceFilter(queryset=PlantaLayout.objects.all(), label='Planta do Layout')

    class Meta:
        model = MaquinaFisica
        # Lista os campos que você quer que o django-filter crie filtros automaticamente
        # ou os que você definiu explicitamente acima.
        fields = ['nome_patrimonio', 'planta_layout', 'tipo_equipamento', 'setor']

class ChamadoFilter(django_filters.FilterSet):
    titulo = django_filters.CharFilter(lookup_expr='icontains', label='Título Contém')
    maquina_fisica__nome_patrimonio = django_filters.CharFilter(lookup_expr='icontains', label='Patrimônio da Máquina')
    status = django_filters.ChoiceFilter(choices=Chamado.StatusChamado.choices, label='Status')
    responsavel_atendimento = django_filters.ModelChoiceFilter(queryset=User.objects.filter(is_staff=True), label='Responsável TI') # Filtra por usuários que são staff
    # Poderia adicionar filtro por data de abertura (DateFromToRangeFilter)

    class Meta:
        model = Chamado
        fields = ['titulo', 'maquina_fisica__nome_patrimonio', 'status', 'responsavel_atendimento']