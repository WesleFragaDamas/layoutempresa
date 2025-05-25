from django.contrib import admin
from .models import PlantaLayout, MaquinaFisica, ConfiguracaoRede, Chamado # Adicionado Chamado
from django.utils import timezone # Certifique-se que timezone está importado

# 1. Classe Admin para o novo modelo PlantaLayout
@admin.register(PlantaLayout)
class PlantaLayoutAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'imagem_fundo', 'data_atualizacao')
    search_fields = ('nome', 'descricao')
    # Se você adicionar campos de largura/altura no modelo PlantaLayout, adicione-os aqui também
    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'imagem_fundo')
        }),
        # ('Dimensões (Opcional)', {
        #     'classes': ('collapse',),
        #     'fields': ('largura_layout', 'altura_layout')
        # }),
        ('Timestamps (Automático)', {
            'classes': ('collapse',),
            'fields': ('data_cadastro', 'data_atualizacao'),
        }),
    )
    readonly_fields = ('data_cadastro', 'data_atualizacao')

# 2. Classe Inline para Configurações de Rede (sem alterações, apenas para contexto)
class ConfiguracaoRedeInline(admin.TabularInline):
    model = ConfiguracaoRede
    extra = 1
    fields = ('ip_address', 'hostname_rede', 'ramal_telefonico', 'codigo_simo', 'ativo', 'observacoes_config')
    readonly_fields = ('data_deteccao', 'ultima_verificacao')

# 3. Classe Admin para MaquinaFisica (MODIFICADA)
@admin.register(MaquinaFisica)
class MaquinaFisicaAdmin(admin.ModelAdmin):
    list_display = (
        'nome_patrimonio',
        'planta_layout', # NOVO CAMPO AQUI
        'mac_address',
        'tipo_equipamento',
        'setor',
        'usuario_responsavel',
        'posicao_x',
        'posicao_y',
        'get_ip_ativo',
        'tipo_equipamento',
    )
    list_filter = ('planta_layout', 'tipo_equipamento', 'setor', 'usuario_responsavel') # Adicionado filtro por planta_layout
    search_fields = ('nome_patrimonio', 'mac_address', 'observacoes_hardware', 'configuracoes_rede__ip_address', 'planta_layout__nome') # Busca no nome da planta
    autocomplete_fields = ['planta_layout', 'usuario_responsavel'] # Adicionado autocomplete para planta_layout
    fieldsets = (
        (None, {
            # Adicionado planta_layout ao fieldset principal
            'fields': ('nome_patrimonio', 'planta_layout', 'mac_address', 'tipo_equipamento')
        }),
        ('Detalhes e Localização (Dentro da Planta)', { # Ajustado o título do fieldset
            'fields': ('setor', 'usuario_responsavel', 'observacoes_hardware')
        }),
        ('Posicionamento no Layout (Dentro da Planta)', { # Ajustado o título do fieldset
            'fields': ('posicao_x', 'posicao_y'),
        }),
    )
    inlines = [ConfiguracaoRedeInline]

    @admin.display(description='IP Ativo')
    def get_ip_ativo(self, obj):
        config_ativa = obj.configuracoes_rede.filter(ativo=True).first()
        return config_ativa.ip_address if config_ativa else "Nenhum IP ativo"

# 4. Classe Admin para ConfiguracaoRede (sem alterações, apenas para contexto)
@admin.register(ConfiguracaoRede)
class ConfiguracaoRedeAdmin(admin.ModelAdmin):
    list_display = ('maquina_fisica', 'ip_address', 'hostname_rede', 'ramal_telefonico', 'ativo', 'ultima_verificacao')
    list_filter = ('ativo', 'maquina_fisica__setor', 'maquina_fisica__planta_layout') # Adicionado filtro por planta_layout da máquina
    search_fields = ('ip_address', 'hostname_rede', 'ramal_telefonico', 'codigo_simo', 'maquina_fisica__nome_patrimonio')
    autocomplete_fields = ['maquina_fisica']
    list_editable = ['ativo']
    fieldsets = (
        (None, {
            'fields': ('maquina_fisica', 'ip_address', 'hostname_rede', 'ativo')
        }),
        ('Informações Vinculadas à Configuração', {
            'fields': ('ramal_telefonico', 'codigo_simo', 'login_padrao_sistema_a', 'senha_padrao_sistema_a', 'observacoes_config')
        }),
        ('Timestamps (Automático)', {
            'classes': ('collapse',),
            'fields': ('data_deteccao', 'ultima_verificacao'),
        }),
    )
    readonly_fields = ('data_deteccao', 'ultima_verificacao')

@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'maquina_fisica', 'status', 'usuario_reportou', 'responsavel_atendimento',
                    'data_abertura', 'data_ultima_atualizacao')
    list_filter = ('status', 'maquina_fisica__planta_layout', 'maquina_fisica', 'responsavel_atendimento',
                   'data_abertura')
    search_fields = ('titulo', 'descricao_problema', 'maquina_fisica__nome_patrimonio',
                     'usuario_reportou__username')
    list_editable = ('status', 'responsavel_atendimento')  # Permite editar estes campos na lista
    autocomplete_fields = ['maquina_fisica', 'usuario_reportou', 'responsavel_atendimento']
    readonly_fields = ('data_abertura', 'data_ultima_atualizacao')

    fieldsets = (
        (None, {
            'fields': ('maquina_fisica', 'titulo', 'descricao_problema')
        }),
        ('Status e Atribuição', {
            'fields': ('status', 'usuario_reportou', 'responsavel_atendimento')
        }),
        ('Resolução (Preencher ao fechar)', {
            'classes': ('collapse',),  # Começa recolhido
            'fields': ('solucao_aplicada', 'data_fechamento')
        }),
        ('Datas (Automático)', {
            'classes': ('collapse',),
            'fields': ('data_abertura', 'data_ultima_atualizacao')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Se o chamado está sendo criado e não tem um usuário reportou, define como o usuário logado
        if not obj.pk and not obj.usuario_reportou:
            obj.usuario_reportou = request.user
        # Se o status está mudando para Resolvido ou Fechado e não tem data de fechamento, define agora
        if obj.status in [Chamado.StatusChamado.RESOLVIDO,
                          Chamado.StatusChamado.FECHADO] and not obj.data_fechamento:
            obj.data_fechamento = timezone.now()
        super().save_model(request, obj, form, change)