from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Colaborador(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    departamento = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} - {self.departamento}"


class Motorista(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    nome = models.CharField(max_length=150)
    cnh = models.CharField(max_length=20, unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} (CNH: {self.cnh})"


class Veiculo(models.Model):
    TIPO_CHOICES = [
        ('leve', 'Leve (Até 4 passageiros)'),
        ('coletivo', 'Coletivo (Até 18 passageiros)'),
    ]
    placa = models.CharField(max_length=10, unique=True)
    modelo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    capacidade_maxima = models.IntegerField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.modelo} [{self.placa}]"


class Reserva(models.Model):
    STATUS_CHOICES = [
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    solicitante = models.ForeignKey(Colaborador, on_delete=models.CASCADE)
    motorista = models.ForeignKey(Motorista, on_delete=models.SET_NULL, null=True, blank=True)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT)
    
    setor = models.CharField(max_length=100)
    atividade = models.CharField(max_length=150)
    origem = models.CharField(max_length=150)
    destino = models.CharField(max_length=150)
    
    data = models.DateField()
    horario_saida = models.TimeField()
    horario_retorno = models.TimeField()
    
    quantidade_passageiros = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmada')
    observacoes = models.TextField(blank=True, null=True)
    protocolo_unico = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def clean(self):
        super().clean()
        
        
        if self.horario_saida and self.horario_retorno:
            if self.horario_retorno <= self.horario_saida:
                raise ValidationError("O horário de retorno deve ser posterior ao horário de saída.")
        
        if self.veiculo and self.quantidade_passageiros:
            if self.quantidade_passageiros > 18:
                raise ValidationError("Solicitações acima de 18 passageiros devem ser rejeitadas.")
            if self.veiculo.tipo == 'leve' and self.quantidade_passageiros > 4:
                raise ValidationError("Veículos leves suportam no máximo 4 passageiros.")

        
        if self.veiculo and self.data and self.horario_saida and self.horario_retorno:
            conflitos = Reserva.objects.filter(
                veiculo=self.veiculo,
                data=self.data,
                status='confirmada',
                horario_saida__lt=self.horario_retorno,
                horario_retorno__gt=self.horario_saida
            )
            
            if self.pk:
                conflitos = conflitos.exclude(pk=self.pk)
                
            if conflitos.exists():
                raise ValidationError("Conflito! Este veículo já está reservado neste período.")