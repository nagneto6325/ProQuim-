from repositories.quimico_repository import QuimicoRepository
from patrones import observable_inventario

class InventarioService:
    @staticmethod
    def get_all():
        return QuimicoRepository.get_all()

    @staticmethod
    def actualizar_stock(quimico_id, nueva_cantidad):
        item = QuimicoRepository.get_by_id(quimico_id)
        if not item:
            return {'success': False, 'error': 'Quimico no encontrado'}

        QuimicoRepository.update_cantidad(quimico_id, nueva_cantidad)

        # Observer: notificar a todos los suscriptores si el stock quedo bajo.
        item_actualizado = dict(item)
        item_actualizado['cantidad'] = nueva_cantidad
        observable_inventario.verificar(item_actualizado)

        # Persistir la alerta en BD cuando el Observer la detecta
        if nueva_cantidad < item['stock_minimo']:
            mensaje = (
                f"Stock bajo: {item['nombre']} tiene {nueva_cantidad} "
                f"{item['unidad']} (minimo: {item['stock_minimo']})"
            )
            QuimicoRepository.crear_alerta(quimico_id, mensaje)
            return {'success': True, 'alerta': mensaje}

        return {'success': True, 'alerta': None}

    @staticmethod
    def get_alertas():
        return QuimicoRepository.get_alertas_no_leidas()

    @staticmethod
    def verificar_stock_suficiente(requerimientos):
        faltantes = []
        for req in requerimientos:
            quimico = QuimicoRepository.get_by_nombre(req['nombre'])
            if not quimico or quimico['cantidad'] < req['cantidad_necesaria']:
                faltantes.append({
                    'nombre': req['nombre'],
                    'necesario': req['cantidad_necesaria'],
                    'disponible': quimico['cantidad'] if quimico else 0
                })
        return {'suficiente': len(faltantes) == 0, 'faltantes': faltantes}