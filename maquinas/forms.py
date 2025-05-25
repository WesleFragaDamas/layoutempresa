from django import forms
from .models import PlantaLayout, MaquinaFisica, ConfiguracaoRede

class PlantaLayoutForm(forms.ModelForm):
    class Meta:
        model = PlantaLayout
        fields = ['nome', 'descricao', 'imagem_fundo']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class MaquinaFisicaForm(forms.ModelForm):
    class Meta:
        model = MaquinaFisica
        fields = [
            'planta_layout',
            'nome_patrimonio',
            'mac_address',
            'tipo_equipamento', # Este agora será um dropdown
            'setor',
            'usuario_responsavel',
            'posicao_x',
            'posicao_y',
            'observacoes_hardware',
        ]
        widgets = {
            'observacoes_hardware': forms.Textarea(attrs={'rows': 3}),
            'posicao_x': forms.NumberInput(attrs={'min': 0, 'style': 'width: 100px;'}),
            'posicao_y': forms.NumberInput(attrs={'min': 0, 'style': 'width: 100px;'}),
            # Não é estritamente necessário definir o widget para 'tipo_equipamento'
            # pois o Django já usará um Select widget devido ao 'choices' no modelo.
            # Mas se quisesse adicionar uma opção "vazia" no topo:
            # 'tipo_equipamento': forms.Select(attrs={'class': 'form-control'}, choices=[('', '---------')] + MaquinaFisica.TipoEquipamento.choices)
        }
        labels = {
            'nome_patrimonio': 'Nome/Patrimônio do Equipamento',
            'planta_layout': 'Planta do Layout Associada',
            'tipo_equipamento': 'Tipo do Equipamento',
        }
        help_texts = {
            'posicao_x': 'Coordenada X no layout (pixels). Edite visualmente no layout para maior precisão.',
            'posicao_y': 'Coordenada Y no layout (pixels). Edite visualmente no layout para maior precisão.',
        }