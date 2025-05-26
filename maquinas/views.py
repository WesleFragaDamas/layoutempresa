from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages # IMPORTAR messages
from django.contrib.messages.views import SuccessMessageMixin # IMPORTAR SuccessMessageMixin
from django.utils.html import format_html # Para formatar HTML seguro no contexto
from django.utils.text import Truncator # NOVA IMPORTAÇÃO
import json
import subprocess # Para executar comandos do sistema operacional (ping)
import platform   # Para identificar o sistema operacional
from django.utils import timezone
from django.db import models

from .models import MaquinaFisica, PlantaLayout, ConfiguracaoRede, Chamado
from .forms import PlantaLayoutForm, MaquinaFisicaForm, ChamadoForm
from .filters import PlantaLayoutFilter, MaquinaFisicaFilter, ChamadoFilter

# --- VIEW DO LAYOUT VISUAL ---
@login_required
def exibir_layout_empresa(request, planta_id=None):
    # ... (código da view de layout permanece o mesmo) ...
    todas_as_plantas = PlantaLayout.objects.all(); planta_selecionada = None
    maquinas_no_layout = MaquinaFisica.objects.none()
    if not todas_as_plantas.exists(): pass
    elif planta_id:
        planta_selecionada = get_object_or_404(PlantaLayout, pk=planta_id)
        maquinas_no_layout = MaquinaFisica.objects.filter(planta_layout=planta_selecionada).order_by('nome_patrimonio')
    else:
        planta_selecionada = todas_as_plantas.first()
        if planta_selecionada: maquinas_no_layout = MaquinaFisica.objects.filter(planta_layout=planta_selecionada).order_by('nome_patrimonio')
    for maquina in maquinas_no_layout:
        config_ativa = maquina.configuracoes_rede.filter(ativo=True).first()
        maquina.config_ativa = config_ativa
    context = {
        'titulo_pagina': f"Layout: {planta_selecionada.nome}" if planta_selecionada else "Layout da Empresa",
        'todas_as_plantas': todas_as_plantas, 'planta_selecionada': planta_selecionada, 'maquinas_fisicas': maquinas_no_layout,
    }
    return render(request, 'maquinas/layout_empresa.html', context)

# --- VIEW AJAX PARA ATUALIZAR POSIÇÃO ---
@login_required
@require_POST
def atualizar_posicao_maquina(request):
    # ... (código da view de atualizar posição permanece o mesmo) ...
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body); maquina_id = data.get('id'); nova_x = data.get('posicao_x'); nova_y = data.get('posicao_y')
            if maquina_id is None or nova_x is None or nova_y is None: return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)
            maquina = get_object_or_404(MaquinaFisica, pk=maquina_id)
            maquina.posicao_x = int(nova_x); maquina.posicao_y = int(nova_y); maquina.save()
            return JsonResponse({'status': 'success', 'message': 'Posição atualizada!'})
        except Exception as e: return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Requisição inválida.'}, status=400)

# --- VIEW AJAX PARA CRIAR CHAMADO ---
@login_required
@require_POST
def criar_chamado_ajax(request):
    # ... (código da view de criar chamado ajax permanece o mesmo) ...
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body); maquina_id = data.get('maquina_id'); titulo = data.get('titulo'); descricao_problema = data.get('descricao_problema')
            if not all([maquina_id, titulo, descricao_problema]): return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)
            if not titulo.strip(): return JsonResponse({'status': 'error', 'message': 'Título não pode ser vazio.'}, status=400)
            if not descricao_problema.strip(): return JsonResponse({'status': 'error', 'message': 'Descrição não pode ser vazia.'}, status=400)
            maquina = get_object_or_404(MaquinaFisica, pk=maquina_id)
            Chamado.objects.create(maquina_fisica=maquina, titulo=titulo.strip(), descricao_problema=descricao_problema.strip(), usuario_reportou=request.user, status=Chamado.StatusChamado.ABERTO)
            return JsonResponse({'status': 'success', 'message': 'Chamado criado!'})
        except Exception as e: import traceback; traceback.print_exc(); return JsonResponse({'status': 'error', 'message': f'Erro: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Inválido.'}, status=400)


@login_required
def verificar_status_maquina_ajax(request, maquina_id):
    maquina = get_object_or_404(MaquinaFisica, pk=maquina_id)
    config_ativa = maquina.configuracoes_rede.filter(ativo=True).first()
    status_online = False
    mensagem = "Configuração de rede ativa não encontrada ou sem IP."

    if config_ativa and config_ativa.ip_address:
        ip = config_ativa.ip_address
        try:
            # Parâmetros do Ping dependem do SO
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            # Comando: ping -n 1 <ip> (Windows) ou ping -c 1 <ip> (Linux/macOS)
            # O timeout também é importante, mas varia. Adicionando um simples:
            # Windows: ping -n 1 -w 1000 <ip> (timeout de 1000ms)
            # Linux: ping -c 1 -W 1 <ip> (timeout de 1 segundo)

            # Construindo o comando de forma mais segura (evitando shell=True se possível)
            if platform.system().lower() == 'windows':
                comando = ['ping', param, '1', '-w', '1000', ip]  # Timeout de 1000 ms
            else:
                comando = ['ping', param, '1', '-W', '1', ip]  # Timeout de 1 segundo

            # Executa o comando ping
            # shell=True é geralmente um risco de segurança se 'ip' vier de input do usuário não sanitizado.
            # Aqui, 'ip' vem do nosso banco, o que é mais seguro, mas o ideal é evitar shell=True.
            # Usar uma lista de argumentos como acima é mais seguro.
            # Para subprocess.call, 0 indica sucesso.
            # Usaremos subprocess.run para melhor controle e captura de saída se necessário.

            resultado = subprocess.run(comando, capture_output=True, text=True,
                                       timeout=2)  # Timeout de 2s para o subprocesso

            if resultado.returncode == 0:
                status_online = True
                mensagem = f"Máquina {ip} está online."
            else:
                status_online = False
                mensagem = f"Máquina {ip} parece estar offline ou não respondeu ao ping."
                # print(f"Erro ping: {resultado.stderr}") # Para depuração

        except subprocess.TimeoutExpired:
            status_online = False
            mensagem = f"Ping para {ip} excedeu o tempo limite."
        except Exception as e:
            status_online = False
            mensagem = f"Erro ao tentar pingar {ip}: {str(e)}"
            # print(f"Exceção no ping: {str(e)}") # Para depuração

        # Atualizar o modelo (opcional, mas útil)
        config_ativa.ultimo_status_online = status_online
        config_ativa.data_ultima_verificacao_status = timezone.now()
        config_ativa.save(update_fields=['ultimo_status_online', 'data_ultima_verificacao_status'])
    else:
        status_online = None  # Indica que não pôde ser verificado
        mensagem = "Máquina sem IP ativo para verificar."

    return JsonResponse({
        'maquina_id': maquina.id,
        'ip_verificado': config_ativa.ip_address if config_ativa else None,
        'online': status_online,
        'mensagem': mensagem,
        'ultima_verificacao': config_ativa.data_ultima_verificacao_status.strftime(
            "%d/%m/%Y %H:%M:%S") if config_ativa and config_ativa.data_ultima_verificacao_status else "Nunca"
    })

# === CRUD PARA PLANTALAYOUT ===
class PlantaLayoutListView(LoginRequiredMixin, ListView):
    model = PlantaLayout; template_name = 'maquinas/plantalayout_list.html'; context_object_name = 'plantas'; paginate_by = 10
    def get_queryset(self): queryset = super().get_queryset().order_by('nome'); self.filterset = PlantaLayoutFilter(self.request.GET, queryset=queryset); return self.filterset.qs
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['filter'] = self.filterset; context['titulo_pagina'] = 'Gerenciar Plantas de Layout'; return context

class PlantaLayoutCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = PlantaLayout; form_class = PlantaLayoutForm; template_name = 'maquinas/_generic_form.html'; success_url = reverse_lazy('maquinas:plantalayout_list')
    success_message = "Planta de layout '%(nome)s' criada com sucesso!"
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['view_title'] = 'Adicionar Nova Planta'; context['submit_button_text'] = 'Criar Planta'; context['cancel_url'] = self.success_url; context['form_id'] = 'planta-create-form'; return context

class PlantaLayoutUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = PlantaLayout; form_class = PlantaLayoutForm; template_name = 'maquinas/_generic_form.html'; success_url = reverse_lazy('maquinas:plantalayout_list')
    success_message = "Planta de layout '%(nome)s' atualizada com sucesso!"
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['view_title'] = f'Editar Planta: {self.object.nome}'; context['submit_button_text'] = 'Salvar Alterações'; context['cancel_url'] = self.success_url; context['form_id'] = f'planta-edit-form-{self.object.pk}'; return context

class PlantaLayoutDeleteView(LoginRequiredMixin, DeleteView):
    model = PlantaLayout; template_name = 'maquinas/plantalayout_confirm_delete.html'; success_url = reverse_lazy('maquinas:plantalayout_list')
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['titulo_pagina'] = 'Confirmar Exclusão de Planta'; return context
    def form_valid(self, form): messages.success(self.request, f"A planta '{self.object.nome}' foi excluída com sucesso."); return super().form_valid(form)

# === CRUD PARA MAQUINAFISICA ===
class MaquinaFisicaListView(LoginRequiredMixin, ListView):
    model = MaquinaFisica; template_name = 'maquinas/maquinafisica_list.html'; context_object_name = 'maquinas'; paginate_by = 10
    def get_queryset(self): queryset = super().get_queryset().select_related('planta_layout', 'usuario_responsavel').order_by('planta_layout', 'nome_patrimonio'); self.filterset = MaquinaFisicaFilter(self.request.GET, queryset=queryset); return self.filterset.qs
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['filter'] = self.filterset; context['titulo_pagina'] = 'Gerenciar Máquinas Físicas'; return context

class MaquinaFisicaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = MaquinaFisica; form_class = MaquinaFisicaForm; template_name = 'maquinas/_generic_form.html'; success_url = reverse_lazy('maquinas:maquinafisica_list')
    success_message = "Máquina '%(nome_patrimonio)s' criada com sucesso!"
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['view_title'] = 'Adicionar Nova Máquina Física'; context['submit_button_text'] = 'Criar Máquina'; context['cancel_url'] = self.success_url; context['form_id'] = 'maquina-create-form'; return context

class MaquinaFisicaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MaquinaFisica; form_class = MaquinaFisicaForm; template_name = 'maquinas/_generic_form.html'; success_url = reverse_lazy('maquinas:maquinafisica_list')
    success_message = "Máquina '%(nome_patrimonio)s' atualizada com sucesso!"
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['view_title'] = f'Editar Máquina: {self.object.nome_patrimonio}'; context['submit_button_text'] = 'Salvar Alterações'; context['cancel_url'] = self.success_url; context['form_id'] = f'maquina-edit-form-{self.object.pk}'; return context

class MaquinaFisicaDeleteView(LoginRequiredMixin, DeleteView):
    model = MaquinaFisica; template_name = 'maquinas/maquinafisica_confirm_delete.html'; success_url = reverse_lazy('maquinas:maquinafisica_list')
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['titulo_pagina'] = 'Confirmar Exclusão de Máquina'; return context
    def form_valid(self, form): messages.success(self.request, f"A máquina '{self.object.nome_patrimonio}' foi excluída com sucesso."); return super().form_valid(form)

# === CRUD PARA CHAMADO ===
class ChamadoListView(LoginRequiredMixin, ListView):
    model = Chamado; template_name = 'maquinas/chamado_list.html'; context_object_name = 'chamados'; paginate_by = 15
    def get_queryset(self):
        queryset = super().get_queryset().select_related('maquina_fisica','maquina_fisica__planta_layout','usuario_reportou','responsavel_atendimento').order_by(models.Case(models.When(status=Chamado.StatusChamado.ABERTO, then=models.Value(0)), models.When(status=Chamado.StatusChamado.EM_ANDAMENTO, then=models.Value(1)), models.When(status=Chamado.StatusChamado.AGUARDANDO_PECA, then=models.Value(2)), models.When(status=Chamado.StatusChamado.AGUARDANDO_TERCEIRO, then=models.Value(3)), default=models.Value(4)),'-data_abertura')
        self.filterset = ChamadoFilter(self.request.GET, queryset=queryset); return self.filterset.qs
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['filter'] = self.filterset; context['titulo_pagina'] = 'Gerenciar Chamados / Incidentes'; return context


class ChamadoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Chamado
    form_class = ChamadoForm
    template_name = 'maquinas/_generic_form.html'
    success_url = reverse_lazy('maquinas:chamado_list')
    success_message = "Chamado #%(id)s atualizado com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chamado = self.object

        # Truncar o título usando Truncator
        truncated_titulo = Truncator(chamado.titulo).chars(30)  # Trunca para 30 caracteres
        context['view_title'] = f'Editar Chamado #{chamado.pk} - {truncated_titulo}'

        context['submit_button_text'] = 'Salvar Alterações'
        context['cancel_url'] = self.success_url
        context['form_id'] = f'chamado-edit-form-{chamado.pk}'
        context['form_pre_content_html'] = format_html(
            # ... (seu format_html existente para os detalhes do chamado) ...
            '<div class="mb-3 p-3 bg-light border rounded">'
            '<h5 class="mb-1">Detalhes da Máquina:</h5>'
            '<p class="mb-1"><strong>Patrimônio:</strong> {}</p>'
            '<p class="mb-1"><strong>Planta:</strong> {}</p>'
            '</div>'
            '<div class="mb-3 p-3 bg-light border rounded">'
            '<h5 class="mb-1">Informações do Chamado:</h5>'
            '<p class="mb-1"><strong>Reportado por:</strong> {}</p>'
            '<p class="mb-0"><strong>Aberto em:</strong> {}</p>'
            '</div>',
            chamado.maquina_fisica.nome_patrimonio,
            chamado.maquina_fisica.planta_layout.nome if chamado.maquina_fisica.planta_layout else "N/A",
            chamado.usuario_reportou.username if chamado.usuario_reportou else "Sistema",
            chamado.data_abertura.strftime("%d/%m/%Y %H:%M") if chamado.data_abertura else "-"
        )
        return context

    def form_valid(self, form):
        # ... (lógica de data_fechamento como antes) ...
        chamado = form.save(commit=False)
        if chamado.status in [Chamado.StatusChamado.RESOLVIDO, Chamado.StatusChamado.FECHADO]:
            if not chamado.data_fechamento: chamado.data_fechamento = timezone.now()
        else:
            chamado.data_fechamento = None
        chamado.save()
        # Ajuste na mensagem de sucesso para usar o título completo ou o truncado se desejar
        messages.success(self.request,
                         self.success_message % {'id': chamado.pk, 'titulo': Truncator(chamado.titulo).chars(30)})
        return super().form_valid(form)

# Adicionar ChamadoDeleteView se necessário no futuro