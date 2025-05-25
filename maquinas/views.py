from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import json

from .models import MaquinaFisica, PlantaLayout, ConfiguracaoRede, Chamado
from .forms import PlantaLayoutForm, MaquinaFisicaForm
from .filters import PlantaLayoutFilter, MaquinaFisicaFilter # NOVA IMPORTAÇÃO

# View existente para exibir o layout
@login_required
def exibir_layout_empresa(request, planta_id=None):
    # ... (código da view de layout permanece o mesmo) ...
    todas_as_plantas = PlantaLayout.objects.all()
    planta_selecionada = None
    MaquinaFisica.objects.filter(planta_layout=planta_selecionada).order_by('nome_patrimonio')
    if not todas_as_plantas.exists(): pass
    elif planta_id:
        planta_selecionada = get_object_or_404(PlantaLayout, pk=planta_id)
        maquinas_no_layout = MaquinaFisica.objects.filter(planta_layout=planta_selecionada).order_by('nome_patrimonio')
    else:
        planta_selecionada = todas_as_plantas.first()
        if planta_selecionada:
            maquinas_no_layout = MaquinaFisica.objects.filter(planta_layout=planta_selecionada).order_by('nome_patrimonio')
    for maquina in maquinas_no_layout:
        config_ativa = maquina.configuracoes_rede.filter(ativo=True).first()
        maquina.config_ativa = config_ativa
    context = {
        'titulo_pagina': f"Layout: {planta_selecionada.nome}" if planta_selecionada else "Layout da Empresa",
        'todas_as_plantas': todas_as_plantas,
        'planta_selecionada': planta_selecionada,
        'maquinas_fisicas': maquinas_no_layout,
    }
    return render(request, 'maquinas/layout_empresa.html', context)


@login_required
@require_POST
def atualizar_posicao_maquina(request):
    # ... (código da view de atualizar posição permanece o mesmo) ...
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            maquina_id = data.get('id'); nova_x = data.get('posicao_x'); nova_y = data.get('posicao_y')
            if maquina_id is None or nova_x is None or nova_y is None: return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)
            maquina = get_object_or_404(MaquinaFisica, pk=maquina_id)
            maquina.posicao_x = int(nova_x); maquina.posicao_y = int(nova_y)
            maquina.save()
            return JsonResponse({'status': 'success', 'message': 'Posição atualizada!'})
        except Exception as e: return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Requisição inválida.'}, status=400)

# ... (criar chamados) ...

@login_required
@require_POST # Só aceita POST
def criar_chamado_ajax(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': # Verifica se é AJAX
        try:
            data = json.loads(request.body)
            maquina_id = data.get('maquina_id')
            titulo = data.get('titulo')
            descricao_problema = data.get('descricao_problema')

            if not all([maquina_id, titulo, descricao_problema]):
                return JsonResponse({'status': 'error', 'message': 'Dados incompletos para criar o chamado.'}, status=400)

            maquina = get_object_or_404(MaquinaFisica, pk=maquina_id)

            Chamado.objects.create(
                maquina_fisica=maquina,
                titulo=titulo,
                descricao_problema=descricao_problema,
                usuario_reportou=request.user, # Associa o usuário logado
                status=Chamado.StatusChamado.ABERTO
            )
            return JsonResponse({'status': 'success', 'message': 'Chamado criado com sucesso!'})
        except MaquinaFisica.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Máquina não encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Requisição inválida.'}, status=400)

# --- VIEWS PARA CRUD DE PLANTALAYOUT (MODIFICADA PlantaLayoutListView) ---
class PlantaLayoutListView(LoginRequiredMixin, ListView):
    model = PlantaLayout
    template_name = 'maquinas/plantalayout_list.html'
    context_object_name = 'plantas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('nome')
        self.filterset = PlantaLayoutFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs # Retorna o queryset filtrado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset # Passa o objeto filterset para o template
        context['titulo_pagina'] = 'Gerenciar Plantas de Layout' # Adicionado título aqui
        return context

class PlantaLayoutCreateView(LoginRequiredMixin, CreateView): # ... (sem alterações) ...
    model = PlantaLayout; form_class = PlantaLayoutForm; template_name = 'maquinas/plantalayout_form.html'; success_url = reverse_lazy('maquinas:plantalayout_list')
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['titulo_formulario'] = 'Adicionar Nova Planta de Layout'; return context
class PlantaLayoutUpdateView(LoginRequiredMixin, UpdateView): # ... (sem alterações) ...
    model = PlantaLayout; form_class = PlantaLayoutForm; template_name = 'maquinas/plantalayout_form.html'; success_url = reverse_lazy('maquinas:plantalayout_list')
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['titulo_formulario'] = 'Editar Planta de Layout'; return context
class PlantaLayoutDeleteView(LoginRequiredMixin, DeleteView): # ... (sem alterações) ...
    model = PlantaLayout; template_name = 'maquinas/plantalayout_confirm_delete.html'; success_url = reverse_lazy('maquinas:plantalayout_list')
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['titulo_pagina'] = 'Confirmar Exclusão de Planta'; return context

# --- VIEWS PARA CRUD DE MAQUINAFISICA (MODIFICADA MaquinaFisicaListView) ---
class MaquinaFisicaListView(LoginRequiredMixin, ListView):
    model = MaquinaFisica
    template_name = 'maquinas/maquinafisica_list.html'
    context_object_name = 'maquinas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('planta_layout', 'usuario_responsavel').order_by('planta_layout', 'nome_patrimonio')
        self.filterset = MaquinaFisicaFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['titulo_pagina'] = 'Gerenciar Máquinas Físicas' # Adicionado título aqui
        return context

class MaquinaFisicaCreateView(LoginRequiredMixin, CreateView): # ... (sem alterações) ...
    model = MaquinaFisica; form_class = MaquinaFisicaForm; template_name = 'maquinas/maquinafisica_form.html'; success_url = reverse_lazy('maquinas:maquinafisica_list')
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['titulo_formulario'] = 'Adicionar Nova Máquina Física'; return context
class MaquinaFisicaUpdateView(LoginRequiredMixin, UpdateView): # ... (sem alterações) ...
    model = MaquinaFisica; form_class = MaquinaFisicaForm; template_name = 'maquinas/maquinafisica_form.html'; success_url = reverse_lazy('maquinas:maquinafisica_list')
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['titulo_formulario'] = 'Editar Máquina Física'; return context
class MaquinaFisicaDeleteView(LoginRequiredMixin, DeleteView): # ... (sem alterações) ...
    model = MaquinaFisica; template_name = 'maquinas/maquinafisica_confirm_delete.html'; success_url = reverse_lazy('maquinas:maquinafisica_list')
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['titulo_pagina'] = 'Confirmar Exclusão de Máquina'; return context

