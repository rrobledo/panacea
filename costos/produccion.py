from django.db import connection
from django.http import JsonResponse
import itertools
from .models import Programacion, Productos
from datetime import datetime

def get_programacion(request, mes = 7, responsable = None, semana = 0):
    condition = ""
    if responsable is not None and responsable != "Todos":
        condition = f" and pr.responsable = '{responsable}'"
    if semana is None:
        semana = 0

    sql = f"""
         select cp.producto_id as id,
                case when pr.nombre is null then cp.producto_nombre else pr.nombre end as producto_nombre,
                case
                    when extract(month from fecha) = 4 then p.apr2024
                    when extract(month from fecha) = 5 then p.may2024corr
                    when extract(month from fecha) = 6 then p.jun2024corr
                    when extract(month from fecha) = 7 then p.jul2024corr
                    when extract(month from fecha) = 8 then p.aug2024corr
                    when extract(month from fecha) = 9 then p.sep2024corr
                    when extract(month from fecha) = 10 then p.oct2024corr
                    when extract(month from fecha) = 11 then p.nov2024corr
                    when extract(month from fecha) = 12 then p.dec2024corr
                end as planeado,
                pr.responsable,
                to_char(fecha, 'YYYYMMDD') as codigo,
                cp.plan,
                cp.prod
          from costos_programacion cp
            join costos_productos pr
              on pr.id = cp.producto_id
            join planificacion2024 p
                on p.codigo = pr.ref_id::int
         where extract(month from fecha) = {mes}
           and (
            {semana} = 0
            or extract('week' from fecha) - extract('week' from '2024-{str(mes).rjust(2, "0")}-02'::date) + 1 = {semana}
           )
         {condition}
         order by producto_nombre, codigo;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = _dictfetchall(cursor)

    res = []
    for k, g in itertools.groupby(result, lambda x: x.get("id")):
        items = list(g)
        item = {}
        item["id"] = k
        item["producto_nombre"] = items[0].get("producto_nombre")
        item["planeado"] = items[0].get("planeado")
        item["responsable"] = items[0].get("responsable")

        for d in items:
            item[f"{d.get('codigo')}-P"] = d.get('plan')
            item[f"{d.get('codigo')}-E"] = d.get('prod')
        res.append(item)

    return res

def update_programacion(data: []):
    for item in data:
        producto_id = item.get("id")
        responsable = item.get("responsable")
        prod = Productos.objects.get(id=producto_id)
        prod.responsable = responsable
        prod.save()
        for key, value in item.items():
            if key not in ('id', 'responsable', 'planeado'):
                codigo, op = key.split('-')
                fecha = datetime.strptime(codigo, "%Y%m%d")
                prog = Programacion.objects.get(producto_id=producto_id, fecha=fecha)
                if value == "":
                    value = None
                if op == 'P':
                    prog.plan = value
                else:
                    prog.prod = value
                prog.save()
    pass


def get_programacion_columns(request):
    mes = int(request.GET.get("mes", "9"))
    semana = int(request.GET.get("semana", "0"))
    sql = f"""
        select distinct extract('week' from fecha) - extract('week' from '2024-{str(mes).rjust(2, "0")}-02'::date) + 1 as semana,
               case 
                    when extract(dow from fecha::date) = 1 then 'Lun'
                    when extract(dow from fecha::date) = 2 then 'Mar'
                    when extract(dow from fecha::date) = 3 then 'Mie'
                    when extract(dow from fecha::date) = 4 then 'Jue'
                    when extract(dow from fecha::date) = 5 then 'Vie'
                    when extract(dow from fecha::date) = 6 then 'Sab'
                end as dia_de_la_semana,
                to_char(fecha, 'YYYYMMDD') as codigo,
                extract(dow from fecha::date)
          from costos_programacion cp
         where extract(month from fecha) = {mes}
           and (
            {semana} = 0
            or extract('week' from fecha) - extract('week' from '2024-{str(mes).rjust(2, "0")}-02'::date) + 1 = {semana}
           )
         order by codigo;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = _dictfetchall(cursor)

    res = [  {
      "headerName": "",
      "children": [
        { "field": "id", "hide": True },
        { "field": "producto", "hide": True },
        {
          "field": "producto_nombre",
          "width": 200,
          "headerName": "Producto",
          "pinned": "left",
        },
        {
          "field": "planeado",
          "width": 70,
          "headerName": "Plan",
          "pinned": "left",
        },
        {
          "valueGetter": 'parseInt(getValue("planeado") / 4)',
          "width": 70,
          "headerName": "Semanal",
          "pinned": "left",
        },
        {
          "field": "responsable",
          "editable": True,
          "headerName": "Responsable",
          "width": 150,
        },
      ],
    }]

    for k, g in itertools.groupby(result, lambda x: x.get("semana")):
        children = []
        for d in g:
            children.append({
                "headerName": d.get("dia_de_la_semana"),
                "children" : [
                    {
                      "field": f"{d.get('codigo')}-P",
                      "editable": True,
                      "headerName": "P",
                      "cellStyle": { "backgroundColor": "silver" },
                    },
                    {
                      "field": f"{d.get('codigo')}-E",
                      "editable": True,
                      "headerName": "E",
                    },
                ],
            })
        res.append(
            {
                "headerName": f"Semana {k}",
                "children": children
            })

    return JsonResponse(res, safe=False)

def get_produccion_by_category(request):
    mes = int(request.GET.get("mes", "9"))

    sql = f"""
    with prog as (select 
            pr.id,
            pr.ref_id,
            pr.nombre,
            pr.categoria,
            pr.responsable,
            sum(cp.prod) as prod,
            extract(month from cp.fecha) as mes
      from costos_programacion cp
        join costos_productos pr
          on pr.id = cp.producto_id
    where extract(year from cp.fecha) = 2024
      and extract(month from cp.fecha) = {mes}
    group by pr.id, pr.ref_id, nombre, categoria, pr.responsable, extract(month from cp.fecha)),
    data as (select pr.nombre,
            pr.categoria,
            pr.responsable,
            case
                when pr.mes = 4 then p.apr2024
                when pr.mes = 5 then p.may2024corr
                when pr.mes = 6 then p.jun2024corr
                when pr.mes = 7 then p.jul2024corr
                when pr.mes = 8 then p.aug2024corr
                when pr.mes = 9 then p.sep2024corr
                when pr.mes = 10 then p.oct2024corr
                when pr.mes = 11 then p.nov2024corr
                when pr.mes = 12 then p.dec2024corr
            end as plan,
            pr.prod,
            (select coalesce(sum(count), 0)
              from panacea_sales_v2 s
             where s.operation_year = 2024
               and s.operation_month = pr.mes
               and s.product_id = pr.id
            )::int vendido
      from prog pr
        join planificacion2024 p
            on p.codigo = pr.ref_id::int)
    select categoria, 
            sum(plan)::int as planeado, 
            sum(prod)::int as producido,
            sum(vendido)::int as vendido,
            (round(sum(prod)::decimal / sum(plan)::decimal * 100, 2))::float as porcentaje_ejecutado,
            (round(sum(vendido)::decimal / sum(plan)::decimal * 100, 2))::float as porcentaje_vendido
      from data
    group by categoria
    having sum(plan)::decimal > 0
    order by categoria
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = _dictfetchall(cursor)

    return JsonResponse(result, safe=False)

def get_produccion_by_productos(request):
    mes = int(request.GET.get("mes", "9"))

    sql = f"""
    with prog as (select 
            pr.id,
            pr.ref_id,
            pr.nombre,
            pr.categoria,
            pr.responsable,
            sum(cp.prod) as prod,
            extract(month from cp.fecha) as mes
      from costos_programacion cp
        join costos_productos pr
          on pr.id = cp.producto_id
    where extract(year from cp.fecha) = 2024
      and extract(month from cp.fecha) = {mes}
    group by pr.id, pr.ref_id, nombre, categoria, pr.responsable, extract(month from cp.fecha)),
    data as (select pr.nombre,
            pr.id,
            pr.mes,
            pr.categoria,
            pr.responsable,
            case
                when pr.mes = 4 then p.apr2024
                when pr.mes = 5 then p.may2024corr
                when pr.mes = 6 then p.jun2024corr
                when pr.mes = 7 then p.jul2024corr
                when pr.mes = 8 then p.aug2024corr
                when pr.mes = 9 then p.sep2024corr
                when pr.mes = 10 then p.oct2024corr
                when pr.mes = 11 then p.nov2024corr
                when pr.mes = 12 then p.dec2024corr
            end as plan,
            pr.prod,
            (select coalesce(sum(count), 0)
              from panacea_sales_v2 s
             where s.operation_year = 2024
               and s.operation_month = pr.mes
               and s.product_id = pr.id
            )::int vendido
      from prog pr
        join planificacion2024 p
            on p.codigo = pr.ref_id::int)
    select  categoria, 
            nombre as producto,
            sum(plan)::int as planeado, 
            sum(prod)::int as producido,
            sum(vendido)::int as vendido,
            (round(sum(prod)::decimal / sum(plan)::decimal * 100, 2))::float as porcentaje_ejecutado,
            (round(sum(vendido)::decimal / sum(plan)::decimal * 100, 2))::float as porcentaje_vendido
      from data
    group by categoria, nombre
    having sum(distinct plan)::decimal > 0
    order by categoria, nombre
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = _dictfetchall(cursor)

    return JsonResponse(result, safe=False)



def get_insumos_by_month(request):
    mes = int(request.GET.get("mes", "9"))
    semana = int(request.GET.get("semana", "0"))
    by_week = request.GET.get("by_week", "yes")

    sql_base = f"""
        with prog as (select 
                cp.producto_id,
                pr.id,
                pr.ref_id,
                pr.nombre,
                pr.categoria,
                pr.responsable,
                sum(cp.prod) as prod,
                sum(cp.plan) as plan,
                extract(month from cp.fecha) as mes,
                extract('week' from fecha) - extract('week' from '2024-{str(mes).rjust(2, "0")}-02'::date) + 1 as semana
          from costos_programacion cp
            join costos_productos pr
              on pr.id = cp.producto_id
        where extract(year from cp.fecha) = 2024
          and extract(month from cp.fecha) = {mes}
        group by cp.producto_id, pr.id, pr.ref_id, nombre, categoria, pr.responsable, extract(month from cp.fecha), semana),
        data as (select pr.producto_id,
                pr.nombre,
                pr.categoria,
                pr.responsable,
                case
                    when pr.mes = 4 then p.apr2024
                    when pr.mes = 5 then p.may2024corr
                    when pr.mes = 6 then p.jun2024corr
                    when pr.mes = 7 then p.jul2024corr
                    when pr.mes = 8 then p.aug2024corr
                    when pr.mes = 9 then p.sep2024corr
                    when pr.mes = 10 then p.oct2024corr
                    when pr.mes = 11 then p.nov2024corr
                    when pr.mes = 12 then p.dec2024corr
                end as plan_mensual,
                pr.plan,
                pr.prod,
                mes,
                semana
          from prog pr
            join planificacion2024 p
                on p.codigo = pr.ref_id::int)
                """
    if by_week == "yes":
        sql = f"""
            {sql_base}
            , res as (      
                select  semana, 
                        ci.nombre as insumo,
                        round(sum(cc.cantidad::decimal / p.lote_produccion::decimal * d.plan::decimal), 2) as plan,  
                        round(sum(cc.cantidad::decimal / p.lote_produccion::decimal * d.prod::decimal), 2) as usado,
                        round((sum(cc.cantidad::decimal / p.lote_produccion::decimal * d.plan::decimal) / ci.cantidad * ci.precio)::decimal, 2) as plan_precio,
                        round((sum(cc.cantidad::decimal / p.lote_produccion::decimal * d.prod::decimal) / ci.cantidad * ci.precio)::decimal, 2) as usado_precio
                  from data d
                    join costos_productos p
                      on d.producto_id = p.id
                    join costos_costos cc
                      on d.producto_id = cc.producto_id
                    join costos_insumos ci
                      on ci.id = cc.insumo_id
                where {semana} = 0 or semana = {semana} 
                group by semana, ci.id)
            select semana,
                   insumo,
                   plan,
                   usado,
                   plan_precio,
                   usado_precio
              from res
            union
            select 999,
                   'Total',
                   null,
                   null,
                   sum(plan_precio),
                   sum(usado_precio)
              from res
            order by 1, 2
        """
    else:
        sql = f"""
            {sql_base}
            , res as (      
                select  mes, 
                        ci.nombre as insumo,
                        round(sum(cc.cantidad::decimal / p.lote_produccion::decimal * d.plan::decimal), 2) as plan,  
                        round(sum(cc.cantidad::decimal / p.lote_produccion::decimal * d.prod::decimal), 2) as usado,
                        round((sum(cc.cantidad::decimal / p.lote_produccion::decimal * d.plan::decimal) / ci.cantidad * ci.precio)::decimal, 2) as plan_precio,
                        round((sum(cc.cantidad::decimal / p.lote_produccion::decimal * d.prod::decimal) / ci.cantidad * ci.precio)::decimal, 2) as usado_precio
                  from data d
                    join costos_productos p
                      on d.producto_id = p.id
                    join costos_costos cc
                      on d.producto_id = cc.producto_id
                    join costos_insumos ci
                      on ci.id = cc.insumo_id 
                group by mes, ci.id)
            select mes,
                   insumo,
                   plan,
                   usado,
                   plan_precio,
                   usado_precio
              from res
            union
            select 999,
                   'Total',
                   null,
                   null,
                   sum(plan_precio),
                   sum(usado_precio)
              from res
            order by 1, 2
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
