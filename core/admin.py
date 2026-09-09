from django.contrib import admin
from .models import Colaborador, Motorista, Veiculo, Reserva

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'departamento', 'cpf')

@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnh', 'ativo', 'usuario') 

@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('modelo', 'placa', 'tipo', 'capacidade_maxima', 'ativo')

    
    def has_module_permission(self, request):
        if hasattr(request.user, 'motorista'): 
            return False
        return True

    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False

    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('protocolo_unico', 'solicitante', 'veiculo', 'data', 'horario_saida', 'horario_retorno', 'status')

    
    def get_queryset(self, request):
        qs = super().get_queryset(request) 
        
        
        if request.user.is_superuser or request.user.groups.filter(name='Colaboradores').exists():
            return qs
            
        
        if hasattr(request.user, 'motorista'):
            return qs.filter(motorista=request.user.motorista)
            
        return qs.none() 

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)