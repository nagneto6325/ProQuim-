from repositories.receta_repository import RecetaRepository
from services.validacion_quimica_service import ValidacionQuimicaService

# servicio para manejar las recetas tecnicas
class RecetaService:
    def __init__(self):
        # usa el validador quimico que tiene el patron strategy
        self.validador = ValidacionQuimicaService()
    
    # obtener todas las recetas
    def get_all(self):
        return RecetaRepository.get_all()
    
    # obtener una receta por su id
    def get_by_id(self, receta_id):
        return RecetaRepository.get_by_id(receta_id)
    
    # crear una receta nueva
    # compatible se calcula antes con el validador
    def create(self, nombre, categoria, rendimiento, ingredientes, compatible):
        receta_id = RecetaRepository.create(nombre, categoria, rendimiento, compatible, ingredientes)
        return receta_id
    
    # validar una receta segun el tipo de estrategia elegida
    # tipos: basica, gramaje, completa
    def validar_receta(self, ingredientes, tipo='basica'):
        if tipo == 'gramaje':
            return self.validador.validar_gramaje(ingredientes, 1000)
        elif tipo == 'completa':
            return self.validador.validar_completa(ingredientes, 1000)
        else:
            return self.validador.validar(ingredientes)