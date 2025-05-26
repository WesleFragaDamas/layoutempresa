from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings # Para referenciar o modelo User
from django.utils import timezone # Para data/hora

# NOVO MODELO: PlantaLayout
class PlantaLayout(models.Model):
    nome = models.CharField(
        _("Nome da Planta/Layout"),
        max_length=100,
        unique=True,
        help_text=_("Ex: Joinville - Térreo, Poá - Escritório TI")
    )
    descricao = models.TextField(
        _("Descrição"),
        blank=True,
        null=True
    )
    imagem_fundo = models.ImageField(
        _("Imagem de Fundo (Planta Baixa)"),
        upload_to='plantas_baixas/', # Subpasta dentro de MEDIA_ROOT
        blank=True, # Permitir plantas sem imagem inicialmente
        null=True,
        help_text=_("Faça upload de uma imagem para o fundo do layout.")
    )
    # Você pode adicionar dimensões aqui se quiser que o layout use as dimensões da imagem
    # largura_layout = models.PositiveIntegerField(_("Largura do Layout (px)"), default=1000)
    # altura_layout = models.PositiveIntegerField(_("Altura do Layout (px)"), default=700)

    data_cadastro = models.DateTimeField(_("Data de Cadastro"), auto_now_add=True)
    data_atualizacao = models.DateTimeField(_("Data da Última Atualização"), auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = _("Planta do Layout")
        verbose_name_plural = _("Plantas dos Layouts")
        ordering = ['nome']

class MaquinaFisica(models.Model):
    planta_layout = models.ForeignKey(
        PlantaLayout,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Planta do Layout Associada"),
        related_name="maquinas_fisicas",
        help_text=_("A qual planta ou layout esta máquina pertence."))
    nome_patrimonio = models.CharField(
        _("Nome/Patrimônio"),
        max_length=100,
        unique=True,
        help_text=_("Identificador único do equipamento físico. Ex: PAT00123, LAB01-PC05"))
    mac_address = models.CharField(
        _("Endereço MAC Principal"),
        max_length=17,
        blank=True,
        null=True,
        unique=True,
        help_text=_("MAC Address da placa de rede principal. Ex: 00:1A:2B:3C:4D:5E"))

    tipo_equipamento = models.CharField(
        _("Tipo de Equipamento"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Ex: Desktop, Notebook, Impressora, Servidor")
    )
    setor = models.CharField(
        _("Setor de Localização"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Setor onde o equipamento está fisicamente localizado (dentro da planta)")
    )
    usuario_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Usuário Responsável"),
        help_text=_("Usuário principal ou responsável pelo equipamento")
    )
    observacoes_hardware = models.TextField(
        _("Observações do Hardware"),
        blank=True,
        null=True
    )
    posicao_x = models.IntegerField(
        _("Posição X no Layout"),
        default=10,
        help_text=_("Coordenada X no layout visual (em pixels)")
    )
    posicao_y = models.IntegerField(
        _("Posição Y no Layout"),
        default=10,
        help_text=_("Coordenada Y no layout visual (em pixels)")
    )
    data_cadastro = models.DateTimeField(_("Data de Cadastro"), auto_now_add=True)
    data_atualizacao = models.DateTimeField(_("Data da Última Atualização"), auto_now=True)

    # NOVO MÉTODO
    def tem_chamados_abertos(self):
        # Verifica se existe algum chamado para esta máquina que não esteja Resolvido, Fechado ou Cancelado
        return self.chamados.exclude(
            status__in=[
                Chamado.StatusChamado.RESOLVIDO,
                Chamado.StatusChamado.FECHADO,
                Chamado.StatusChamado.CANCELADO
            ]
        ).exists()

    def __str__(self):
        return self.nome_patrimonio

    class Meta:
        verbose_name = _("Máquina Física")
        verbose_name_plural = _("Máquinas Físicas")
        ordering = ['planta_layout', 'nome_patrimonio']

    # --- DEFINIÇÃO DAS ESCOLHAS PARA TIPO DE EQUIPAMENTO ---
    class TipoEquipamento(models.TextChoices):
        DESKTOP = 'DESKTOP', _('Desktop')
        NOTEBOOK = 'NOTEBOOK', _('Notebook / Laptop')
        IMPRESSORA = 'IMPRESSORA', _('Impressora')
        SERVIDOR = 'SERVIDOR', _('Servidor')
        ROTEADOR = 'ROTEADOR', _('Roteador')
        SWITCH = 'SWITCH', _('Switch de Rede')
        TELEFONE_IP = 'TELEFONE_IP', _('Telefone IP')
        OUTRO = 'OUTRO', _('Outro')
        DESCONHECIDO = 'DESCONHECIDO', _('Desconhecido') # Para o default no template

    tipo_equipamento = models.CharField(
        _("Tipo de Equipamento"),
        max_length=20,  # Deve ser grande o suficiente para o maior valor das escolhas (ex: 'TELEFONE_IP')
        choices=TipoEquipamento.choices,
        default=TipoEquipamento.DESCONHECIDO, # Um valor padrão é bom
        blank=False, # Tornar obrigatório selecionar um tipo
        null=False,  # Não permitir nulo no banco
        help_text=_("Selecione o tipo do equipamento.")
    )
    # ----------------------------------------------------

    setor = models.CharField(
        _("Setor de Localização"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Setor onde o equipamento está fisicamente localizado (dentro da planta)"))
    usuario_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Usuário Responsável"),
        help_text=_("Usuário principal ou responsável pelo equipamento"))
    observacoes_hardware = models.TextField(
        _("Observações do Hardware"),
        blank=True,
        null=True)
    posicao_x = models.IntegerField(
        _("Posição X no Layout"),
        default=10,
        help_text=_("Coordenada X no layout visual (em pixels)"))
    posicao_y = models.IntegerField(
        _("Posição Y no Layout"),
        default=10,
        help_text=_("Coordenada Y no layout visual (em pixels)"))
    data_cadastro = models.DateTimeField(
        _("Data de Cadastro"),
        auto_now_add=True)
    data_atualizacao = models.DateTimeField(
        _("Data da Última Atualização"),
        auto_now=True)
    def __str__(self): return self.nome_patrimonio

    class Meta: verbose_name = (_("Máquina Física"));
    verbose_name_plural = _("Máquinas Físicas");
    ordering = ['planta_layout', 'nome_patrimonio']

class ConfiguracaoRede(models.Model):
    maquina_fisica = models.ForeignKey(
        MaquinaFisica,
        on_delete=models.CASCADE,
        verbose_name=_("Máquina Física Associada"),
        related_name="configuracoes_rede"
    )
    ip_address = models.GenericIPAddressField(
        _("Endereço IP"),
        protocol='both',
        unique=True,
        help_text=_("IP atual da máquina nesta configuração.")
    )
    hostname_rede = models.CharField(
        _("Hostname na Rede"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Nome que a máquina está usando na rede (pode ser diferente do patrimônio)")
    )
    ramal_telefonico = models.CharField(
        _("Ramal Telefônico"),
        max_length=20,
        blank=True,
        null=True
    )
    codigo_simo = models.CharField(
        _("Código SIMO"),
        max_length=50,
        blank=True,
        null=True
    )
    login_padrao_sistema_a = models.CharField(
        _("Login Padrão (Servidor/Acesso Remoto)"), # Ajustei o label
        max_length=100,
        blank=True,
        null=True
    )
    senha_padrao_sistema_a = models.CharField(
        _("Senha Padrão (Servidor/Acesso Remoto)"), # Ajustei o label
        max_length=128,
        blank=True,
        null=True,
        help_text=_("Considere implicações de segurança ao armazenar senhas.")
    )
    ativo = models.BooleanField(
        _("Configuração Ativa?"),
        default=True,
        help_text=_("Marque se esta é a configuração de rede atual para a máquina física.")
    )
    data_deteccao = models.DateTimeField(
        _("Data da Detecção/Cadastro"),
        auto_now_add=True
    )
    ultima_verificacao = models.DateTimeField(
        _("Última Verificação"),
        auto_now=True
    )
    observacoes_config = models.TextField(
        _("Observações da Configuração"),
        blank=True,
        null=True
    )
    ultimo_status_online = models.BooleanField(
        _("Último Status Online"),
        null=True,  # Pode não ter sido verificado ainda
        blank=True,
        default=None  # Ou False se preferir
    )
    data_ultima_verificacao_status = models.DateTimeField(
        _("Data da Última Verificação de Status"),
        null=True,
        blank=True
    )

    def __str__(self):
        status = "Ativo" if self.ativo else "Inativo"
        return f"{self.maquina_fisica.nome_patrimonio} - IP: {self.ip_address} ({status})"

    class Meta:
        verbose_name = _("Configuração de Rede")
        verbose_name_plural = _("Configurações de Rede")
        ordering = ['-ativo', '-data_deteccao']

class Chamado(models.Model):
    class StatusChamado(models.TextChoices):
        ABERTO = 'ABERTO', _('Aberto')
        EM_ANDAMENTO = 'EM_ANDAMENTO', _('Em Andamento')
        AGUARDANDO_PECA = 'AGUARDANDO_PECA', _('Aguardando Peça')
        AGUARDANDO_TERCEIRO = 'AGUARDANDO_TERCEIRO', _('Aguardando Terceiro')
        RESOLVIDO = 'RESOLVIDO', _('Resolvido')
        FECHADO = 'FECHADO', _('Fechado') # Similar a resolvido, mas pode ter fluxo diferente
        CANCELADO = 'CANCELADO', _('Cancelado')

    maquina_fisica = models.ForeignKey(
        MaquinaFisica,
        on_delete=models.CASCADE, # Se a máquina for excluída, seus chamados também são. Considere SET_NULL se quiser manter o histórico.
        related_name='chamados',
        verbose_name=_("Máquina com Problema")
    )
    titulo = models.CharField(
        _("Título do Chamado/Problema"),
        max_length=200,
        help_text=_("Um breve resumo do problema. Ex: 'Computador não liga', 'Impressora atolando papel'")
    )
    descricao_problema = models.TextField(
        _("Descrição Detalhada do Problema")
    )
    status = models.CharField(
        _("Status do Chamado"),
        max_length=20,
        choices=StatusChamado.choices,
        default=StatusChamado.ABERTO
    )
    usuario_reportou = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Se o usuário for deletado, mantém o chamado mas sem o relator
        null=True,
        blank=True, # Pode ser reportado por um sistema ou usuário anônimo inicialmente
        related_name='chamados_reportados',
        verbose_name=_("Reportado Por")
    )
    responsavel_atendimento = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chamados_responsaveis',
        verbose_name=_("Responsável pelo Atendimento (TI)")
    )
    data_abertura = models.DateTimeField(
        _("Data de Abertura"),
        default=timezone.now # Define automaticamente ao criar
    )
    data_ultima_atualizacao = models.DateTimeField(
        _("Última Atualização"),
        auto_now=True # Atualiza automaticamente ao salvar
    )
    data_fechamento = models.DateTimeField(
        _("Data de Fechamento"),
        null=True,
        blank=True
    )
    solucao_aplicada = models.TextField(
        _("Solução Aplicada"),
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Chamado #{self.pk}: {self.titulo} ({self.maquina_fisica.nome_patrimonio})"

    class Meta:
        verbose_name = _("Chamado / Incidente")
        verbose_name_plural = _("Chamados / Incidentes")
        ordering = ['-data_abertura'] # Mais recentes primeiro