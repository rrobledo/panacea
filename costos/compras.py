from django.db import connection
from django.http import JsonResponse
import itertools
from .models import Programacion, Productos, Planificacion
from datetime import datetime

def get_cuenta_corriente_prov_resumen(request):
    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")

    sql = f"""
    with t_total_facturas_pendientes as (
        select round(sum(importe_pendiente)::numeric, 2) as total_facturas_pendientes
          from costos_cuentacorrienteproveedor cc 
         where tipo_movimiento = 'FACTURA'
           and tipo_pago = 'CUENTA_CORRIENTE'
           -- and fecha_emision between '{fecha_desde}' and '{fecha_hasta}' 
        ),
    t_total_gastos as (
        select round(sum(importe_total)::numeric, 2) as total_gastos
          from costos_cuentacorrienteproveedor cc 
         where fecha_emision between '{fecha_desde}' and '{fecha_hasta}'
           and (
                (
                    tipo_movimiento = 'FACTURA'
                    and tipo_pago <> 'CUENTA_CORRIENTE'
                )
                or 
                (
                    tipo_movimiento = 'PAGO'
                )
               )
       )
    select (select total_facturas_pendientes from t_total_facturas_pendientes) as total_facturas_pendientes,
    (select total_gastos from t_total_gastos) as total_gastos
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = _dictfetchall(cursor)

    return JsonResponse(result, safe=False)


def _dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
