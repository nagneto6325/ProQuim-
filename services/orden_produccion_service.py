import sys
import os
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.orden_repository import OrdenRepository
from repositories.receta_repository import RecetaRepository
from repositories.quimico_repository import QuimicoRepository
from patrones import observable_inventario

class OrdenProduccionService:
    @staticmethod
    def get_all():
        ordenes = OrdenRepository.get_all()
        resultado = []
        for orden in ordenes:
            orden_dict = dict(orden) if not isinstance(orden, dict) else orden
            trazabilidad = OrdenRepository.get_trazabilidad_by_orden(orden_dict['id'])
            orden_dict['trazabilidad'] = trazabilidad
            resultado.append(orden_dict)
        return resultado

    @staticmethod
    def calcular_materiales(receta_id, cantidad_producir):
        receta = RecetaRepository.get_by_id(receta_id)
        if not receta:
            return None
        factor = cantidad_producir / receta['rendimiento']
        materiales = []
        for ing in receta['ingredientes']:
            materiales.append({
                'nombre': ing['nombre'],
                'cantidad_necesaria': round(ing['gramos'] * factor, 2)
            })
        return materiales

    @staticmethod
    def crear_orden(receta_id, cantidad_producir):
        receta = RecetaRepository.get_by_id(receta_id)
        if not receta:
            return {'success': False, 'error': 'Receta no encontrada'}

        orden_id = OrdenRepository.create(receta_id, cantidad_producir)
        return {
            'success': True,
            'orden_id': orden_id,
            'mensaje': 'Orden creada exitosamente'
        }

    @staticmethod
    def ejecutar_orden(orden_id, responsable):
        orden = OrdenRepository.get_by_id(orden_id)
        if not orden:
            return {'success': False, 'error': 'Orden no encontrada'}

        if orden['estado'] != 'Pendiente':
            return {'success': False, 'error': f'La orden ya esta {orden["estado"]}'}

        receta = RecetaRepository.get_by_id(orden['receta_id'])
        if not receta:
            return {'success': False, 'error': 'Receta no encontrada'}

        factor = float(orden['cantidad_producir']) / float(receta['rendimiento'])

        for ing in receta['ingredientes']:
            cantidad_a_descontar = float(ing['gramos']) * factor
            quimico = QuimicoRepository.get_by_nombre(ing['nombre'])

            if not quimico:
                return {'success': False, 'error': f'Quimico no encontrado: {ing["nombre"]}'}

            nueva_cantidad = float(quimico['cantidad']) - cantidad_a_descontar

            # Evitar stock negativo
            if nueva_cantidad < 0:
                return {
                    'success': False,
                    'error': f'Stock insuficiente de {ing["nombre"]}: '
                             f'disponible {quimico["cantidad"]}, necesario {round(cantidad_a_descontar, 2)}'
                }

            QuimicoRepository.update_cantidad(quimico['id'], nueva_cantidad)
            OrdenRepository.registrar_consumo(orden_id, quimico['id'], cantidad_a_descontar)

            # Observer: pasar dict para evitar error con sqlite3.Row
            item_actualizado = QuimicoRepository.get_by_id(quimico['id'])
            if item_actualizado:
                observable_inventario.verificar(dict(item_actualizado))

        lote = f"LP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{orden_id}"
        OrdenRepository.registrar_trazabilidad(orden_id, lote, responsable)
        OrdenRepository.update_estado(orden_id, 'Completada')

        return {
            'success': True,
            'lote_produccion': lote,
            'mensaje': f'Orden ejecutada correctamente. Lote: {lote}'
        }