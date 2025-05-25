from django import forms
from .models import PlantaLayout, MaquinaFisica, ConfiguracaoRede, Chamado # Certifique-se que Chamado está importado
from django.contrib.auth import get_user_model

User = get_user_model() # Obter o modelo de usuário ativo do projeto

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
            'tipo_equipamento',
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
        }
        labels = {
            'nome_patrimonio': 'Nome/Patrimônio do Equipamento',
            'planta_layout': 'Planta do Layout Associada',
            'tipo_equipamento': 'Tipo do Equipamento', # Adicionado para consistência, já que tipo_equipamento é um dropdown
        }
        help_texts = {
            'posicao_x': 'Coordenada X no layout (pixels). Edite visualmente no layout para maior precisão.',
            'posicao_y': 'Coordenada Y no layout (pixels). Edite visualmente no layout para maior precisão.',
        }

class ChamadoForm(forms.ModelForm):
    # Customizando o campo para responsavel_atendimento para filtrar usuários
    responsavel_atendimento = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True), # Exemplo: Apenas usuários staff
        required=False, # Opcional, dependendo se um responsável é sempre necessário
        label="Responsável pelo Atendimento (TI)",
        widget=forms.Select(attrs={'class': 'form-control'}) # Opcional: Adiciona uma classe CSS
    )

    class Meta:
        model = Chamado
        fields = [
            'titulo',
            'descricao_problema',
            'status',
            'responsavel_atendimento', # Usará o campo customizado acima
            'solucao_aplicada',
            # Campos como maquina_fisica, usuario_reportou, data_abertura, data_fechamento
            # são geralmente definidos pela view ou automaticamente, e não editados diretamente aqui.
            # Se precisar deles no formulário, adicione-os à lista 'fields'.
        ]
        widgets = {
            'descricao_problema': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'solucao_aplicada': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'titulo': 'Título do Chamado',
            'descricao_problema': 'Descrição Detalhada do Problema',
            'status': 'Status Atual do Chamado',
            'solucao_aplicada': 'Solução Aplicada (se resolvido/fechado)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exemplo de como adicionar uma opção "vazia" ao dropdown de responsável, se 'required=False'
        if 'responsavel_atendimento' in self.fields:
             self.fields['responsavel_atendimento'].empty_label = "Ninguém atribuído"

        # Se você quisesse desabilitar campos na edição (não estamos fazendo isso aqui,
        # pois eles não estão nos 'fields' para serem editados):
        # if self.instance and self.instance.pk: # Se for uma instância existente (edição)
        #     if 'maquina_fisica' in self.fields:
        #         self.fields['maquina_fisica'].disabled = True
        #     if 'usuario_reportou' in self.fields:
        #         self.fields['usuario_reportou'].disabled = True