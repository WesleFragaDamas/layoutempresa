from django.contrib import admin
from .models import MaquinaFisica, ConfiguracaoRede

# 1. Classe Inline para exibir/editar Configurações de Rede DENTRO de MaquinaFisica
class ConfiguracaoRedeInline(admin.TabularInline): # Ou admin.StackedInline para outro layout
    model = ConfiguracaoRede
    extra = 1 # Quantos formulários de ConfigRede em branco mostrar ao criar/editar MaquinaFisica
    fields = (
        'ip_address',
        'hostname_rede',
        'ramal_telefonico',
        'codigo_simo',
        # 'login_padrao_sistema_a', # Descomente se quiser editar inline
        # 'senha_padrao_sistema_a', # Descomente se quiser editar inline (lembre-se do alerta de segurança)
        'ativo',
        'observacoes_config'
    )
    readonly_fields = ('data_deteccao', 'ultima_verificacao')
    # Adicione 'fk_name' se o Django tiver dificuldade em encontrar a chave estrangeira correta,
    # mas para um ForeignKey simples para MaquinaFisica, geralmente não é necessário.
    # fk_name = 'maquina_fisica' # Exemplo, se necessário

# 2. Classe Admin para o modelo MaquinaFisica
@admin.register(MaquinaFisica)
class MaquinaFisicaAdmin(admin.ModelAdmin):
    list_display = (
        'nome_patrimonio',
        'mac_address',
        'tipo_equipamento',
        'setor',
        'usuario_responsavel',
        'posicao_x',
        'posicao_y',
        'get_ip_ativo', # Método para mostrar o IP ativo
    )
    list_filter = ('tipo_equipamento', 'setor', 'usuario_responsavel')
    search_fields = ('nome_patrimonio', 'mac_address', 'observacoes_hardware', 'configuracoes_rede__ip_address')
    fieldsets = (
        (None, {
            'fields': ('nome_patrimonio', 'mac_address', 'tipo_equipamento')
        }),
        ('Detalhes e Localização', {
            'fields': ('setor', 'usuario_responsavel', 'observacoes_hardware')
        }),
        ('Posicionamento no Layout', {
            'fields': ('posicao_x', 'posicao_y'),
        }),
    )
    inlines = [ConfiguracaoRedeInline] # Inclui o inline definido acima

    @admin.display(description='IP Ativo')
    def get_ip_ativo(self, obj):
        config_ativa = obj.configuracoes_rede.filter(ativo=True).first()
        return config_ativa.ip_address if config_ativa else "Nenhum IP ativo"

# 3. Classe Admin para o modelo ConfiguracaoRede (para gerenciar separadamente)
@admin.register(ConfiguracaoRede)
class ConfiguracaoRedeAdmin(admin.ModelAdmin):
    list_display = ('maquina_fisica', 'ip_address', 'hostname_rede', 'ramal_telefonico', 'ativo', 'ultima_verificacao')
    list_filter = ('ativo', 'maquina_fisica__setor') # Filtrar por setor da máquina física associada
    search_fields = ('ip_address', 'hostname_rede', 'ramal_telefonico', 'codigo_simo', 'maquina_fisica__nome_patrimonio')
    autocomplete_fields = ['maquina_fisica'] # Melhora a seleção de MaquinaFisica
    list_editable = ['ativo'] # Permite editar o campo 'ativo' diretamente na lista

    fieldsets = (
        (None, {
            'fields': ('maquina_fisica', 'ip_address', 'hostname_rede', 'ativo')
        }),
        ('Informações Vinculadas à Configuração', {
            'fields': (
                'ramal_telefonico',
                'codigo_simo',
                'login_padrao_sistema_a',
                'senha_padrao_sistema_a', # Lembre-se do alerta de segurança
                'observacoes_config'
                # Adicione mais campos aqui à medida que os criar no models.py
            )
        }),
        ('Timestamps (Automático)', {
            'classes': ('collapse',),
            'fields': ('data_deteccao', 'ultima_verificacao'),
        }),
    )
    readonly_fields = ('data_deteccao', 'ultima_verificacao')