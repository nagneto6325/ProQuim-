from repositories.orden_repository import OrdenRepository
from repositories.receta_repository import RecetaRepository

# servicio de trazabilidad
# junta informacion de orden, receta y consumos para mostrar el historial completo
class TrazabilidadService:
    @staticmethod
    def get_trazabilidad_completa(orden_id):
        # busca la orden por su id
        orden = OrdenRepository.get_by_id(orden_id)
        if not orden:
            return None
        
        # trae la receta que se uso en esa orden
        receta = RecetaRepository.get_by_id(orden['receta_id'])
        
        # trae el lote de produccion (si ya se ejecuto)
        trazabilidad = OrdenRepository.get_trazabilidad_by_orden(orden_id)
        
        # trae la lista de materias primas que se consumieron
        consumos = OrdenRepository.get_consumos_by_orden(orden_id)
        
        # arma un diccionario con toda la informacion
        return {
            'orden': dict(orden),
            'receta': receta,
            'trazabilidad': trazabilidad,
            'consumos': consumos
        }