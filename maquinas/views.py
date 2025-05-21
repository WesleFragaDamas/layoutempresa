from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse # Para responder a requisições AJAX
from django.views.decorators.http import require_POST # Para garantir que a view só aceite POST
import json # Para decodificar o corpo da requisição JSON
from .models import MaquinaFisica

@login_required
def exibir_layout_empresa(request):
    maquinas_no_layout = MaquinaFisica.objects.all().order_by('nome_patrimonio')
    for maquina in maquinas_no_layout:
        config_ativa = maquina.configuracoes_rede.filter(ativo=True).first()
        maquina.config_ativa = config_ativa
    context = {
        'titulo_pagina': 'Layout da Empresa',
        'maquinas_fisicas': maquinas_no_layout,
    }
    return render(request, 'maquinas/layout_empresa.html', context)

@login_required
@require_POST # Esta view só aceitará requisições POST
def atualizar_posicao_maquina(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': # Verifica se é AJAX
        try:
            data = json.loads(request.body)
            maquina_id = data.get('id')
            nova_x = data.get('posicao_x')
            nova_y = data.get('posicao_y')

            if maquina_id is None or nova_x is None or nova_y is None:
                return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)

            maquina = get_object_or_404(MaquinaFisica, pk=maquina_id)
            maquina.posicao_x = int(nova_x)
            maquina.posicao_y = int(nova_y)
            maquina.save()

            return JsonResponse({'status': 'success', 'message': 'Posição atualizada!'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido.'}, status=400)
        except MaquinaFisica.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Máquina não encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Requisição inválida.'}, status=400)