from django.shortcuts import render

from django.http import JsonResponse
from .models import Reserva

def listar_reservas(request):
    # Usando o Django ORM para buscar todas as reservas cadastradas
    reservas = Reserva.objects.all().values(
        'protocolo_unico', 'atividade', 'data', 'horario_saida', 'horario_retorno', 'status'
    )
    # Retorna os dados convertidos em lista JSON
    return JsonResponse(list(reservas), safe=False)

import json
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError

@csrf_exempt 
def criar_reserva(request):
    if request.method == 'POST':
        try:
            
            dados = json.loads(request.body)
            
            veiculo_id = dados.get('veiculo_id')
            data = dados.get('data')
            horario_saida = dados.get('horario_saida')
            horario_retorno = dados.get('horario_retorno')
            
            
            conflitos = Reserva.objects.filter(
                veiculo_id=veiculo_id,
                data=data,
                status='confirmada',
                horario_saida__lt=horario_retorno,
                horario_retorno__gt=horario_saida
            )
            
            if conflitos.exists():
                return JsonResponse({'erro': 'Conflito de horário! Este veículo já está reservado nesse período.'}, status=400)
            
            
            
            return JsonResponse({'sucesso': 'Reserva cadastrada com sucesso!'}, status=201)
            
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)
            
    return JsonResponse({'erro': 'Método não permitido'}, status=405)