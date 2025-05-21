from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings # Para referenciar o modelo User

class MaquinaFisica(models.Model):
    nome_patrimonio = models.CharField(
        _("Nome/Patrimônio"),
        max_length=100,
        unique=True,
        help_text=_("Identificador único do equipamento físico. Ex: PAT00123, LAB01-PC05")
    )
    mac_address = models.CharField(
        _("Endereço MAC Principal"),
        max_length=17,
        blank=True,
        null=True,
        unique=True,
        help_text=_("MAC Address da placa de rede principal. Ex: 00:1A:2B:3C:4D:5E")
    )
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
        help_text=_("Setor onde o equipamento está fisicamente localizado")
    )
    usuario_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Relaciona com o modelo de Usuário do Django
        on_delete=models.SET_NULL, # Se o usuário for deletado, define este campo como nulo
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
    # Campos para a localização no layout
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

    def __str__(self):
        return self.nome_patrimonio

    class Meta:
        verbose_name = _("Máquina Física")
        verbose_name_plural = _("Máquinas Físicas")
        ordering = ['nome_patrimonio']

# ... (importações e MaquinaFisica continuam iguais) ...

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
        unique=True, # Idealmente, um IP ativo é único.
        help_text=_("IP atual da máquina nesta configuração.")
    )
    hostname_rede = models.CharField(
        _("Hostname na Rede"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Nome que a máquina está usando na rede (pode ser diferente do patrimônio)")
    )

    # --- NOVOS CAMPOS VINCULADOS AO IP/CONFIGURAÇÃO ---
    ramal_telefonico = models.CharField(
        _("Ramal Telefônico"),
        max_length=20, # Ajuste o tamanho conforme necessário
        blank=True,
        null=True
    )
    codigo_simo = models.CharField( # Supondo que SIMO seja um código/identificador
        _("Código SIMO"),
        max_length=50,
        blank=True,
        null=True
    )
    login_padrao_sistema_a = models.CharField( # Exemplo para um sistema específico
        _("Login Padrão (Sistema A)"),
        max_length=100,
        blank=True,
        null=True
    )
    senha_padrao_sistema_a = models.CharField( # ATENÇÃO COM SENHAS!
        _("Senha Padrão (Sistema A)"),
        max_length=128, # Para armazenar hashes, não senhas em texto puro
        blank=True,
        null=True,
        help_text=_("Considere implicações de segurança ao armazenar senhas.")
    )
    # Adicione mais campos conforme sua necessidade:
    # Ex:
    # nome_impressora_rede = models.CharField(max_length=100, blank=True, null=True)
    # software_especifico_licenca = models.CharField(max_length=100, blank=True, null=True)
    # ... outros campos ...

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

    def __str__(self):
        status = "Ativo" if self.ativo else "Inativo"
        return f"{self.maquina_fisica.nome_patrimonio} - IP: {self.ip_address} ({status})"

    class Meta:
        verbose_name = _("Configuração de Rede")
        verbose_name_plural = _("Configurações de Rede")
        ordering = ['-ativo', '-data_deteccao']