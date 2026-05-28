import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from patrones import validador_quimico, ValidacionBasica, ValidacionGramaje, ValidacionCompleta

class ValidacionQuimicaService:
    @staticmethod
    def cambiar_estrategia(tipo):
        if tipo == 'gramaje':
            validador_quimico.set_estrategia(ValidacionGramaje())
        elif tipo == 'completa':
            validador_quimico.set_estrategia(ValidacionCompleta())
        else:
            validador_quimico.set_estrategia(ValidacionBasica())
    
    @staticmethod
    def validar(ingredientes):
        return validador_quimico.validar(ingredientes)
    
    @staticmethod
    def validar_gramaje(ingredientes, rendimiento):
        validador_quimico.set_estrategia(ValidacionGramaje())
        return validador_quimico.validar(ingredientes)
    
    @staticmethod
    def validar_completa(ingredientes, rendimiento):
        validador_quimico.set_estrategia(ValidacionCompleta())
        return validador_quimico.validar(ingredientes)