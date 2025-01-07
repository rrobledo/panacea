from django.db import connection
from django.http import JsonResponse
import itertools
from .models import Programacion, Productos, Planificacion
from datetime import datetime

def get_planning(request, anio = 2025):
    sql = f"""
         select cp.producto_id as id,
                pr.nombre as producto_nombre,
                to_char(fecha, 'YYYYMM') as codigo,
                cp.plan,
                cp.sistema,
                cp.corregido,
                (select coalesce(sum(prod), 0)
                   from costos_programacion s
                  where extract(year from s.fecha) = extract(year from cp.fecha)
                    and extract(month from s.fecha) = extract(month from cp.fecha)
                    and s.producto_id = cp.producto_id
                )::int prod,
                (select coalesce(sum(count), 0)
                   from panacea_sales_v2 s
                  where s.operation_year = extract(year from cp.fecha)
                    and s.operation_month = extract(month from cp.fecha)
                    and s.product_id = cp.producto_id
                )::int venta
          from costos_planificacion cp
            join costos_productos pr
              on pr.id = cp.producto_id
             and pr.habilitado = true
          where extract(year from cp.fecha) = {anio}
         union
         select 999 as id,
                'ÑzTOTAL' as producto_nombre,
                to_char(fecha, 'YYYYMM') as codigo,
                sum(cp.plan) as plan,
                sum(cp.sistema) as sistema,
                sum(cp.corregido) as corregido,
                sum((select coalesce(sum(prod), 0)
                   from costos_programacion s
                  where extract(year from s.fecha) = extract(year from cp.fecha)
                    and extract(month from s.fecha) = extract(month from cp.fecha)
                    and s.producto_id = cp.producto_id
                ))::int prod,
                sum((select coalesce(sum(count), 0)
                   from panacea_sales_v2 s
                  where s.operation_year = extract(year from cp.fecha)
                    and s.operation_month = extract(month from cp.fecha)
                    and s.product_id = cp.producto_id
                ))::int venta
          from costos_planificacion cp
            join costos_productos pr
              on pr.id = cp.producto_id
             and pr.habilitado = true
        where extract(year from cp.fecha) = {anio}
        group by to_char(fecha, 'YYYYMM')
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

        for d in items:
            item[f"{d.get('codigo')}-PLAN"] = d.get('plan')
            item[f"{d.get('codigo')}-SISTEMA"] = d.get('sistema')
            item[f"{d.get('codigo')}-CORREGIDO"] = d.get('corregido')
            item[f"{d.get('codigo')}-PROD"] = d.get('prod')
            item[f"{d.get('codigo')}-VENTA"] = d.get('venta')
        res.append(item)

    return res


def get_planning_columns(request):
    anio = int(request.GET.get("anio", 2024))
    sql = f"""
         select distinct extract(month from cp.fecha) as mes,
				case
                    when extract(month from cp.fecha) = 1 then 'Enero'
                    when extract(month from cp.fecha) = 2 then 'Febrero'
                    when extract(month from cp.fecha) = 3 then 'Marzo'
                    when extract(month from cp.fecha) = 4 then 'Abril'
                    when extract(month from cp.fecha) = 5 then 'Mayo'
                    when extract(month from cp.fecha) = 6 then 'Junio'
                    when extract(month from cp.fecha) = 7 then 'Julio'
                    when extract(month from cp.fecha) = 8 then 'Agosto'
                    when extract(month from cp.fecha) = 9 then 'Septiembre'
                    when extract(month from cp.fecha) = 10 then 'Octubre'
                    when extract(month from cp.fecha) = 11 then 'Noviembre'
                    when extract(month from cp.fecha) = 12 then 'Diciembre'
                end as mes_del_anio,
                to_char(fecha, 'YYYYMM') as codigo
          from costos_planificacion cp
            join costos_productos pr
              on pr.id = cp.producto_id
             and pr.habilitado = true
         where extract(year from cp.fecha) = {anio}
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
      ],
    }]

    children = []
    for d in result:
        children.append({
            "headerName": d.get("mes_del_anio"),
            "children" : [
                {
                  "field": f"{d.get('codigo')}-PLAN",
                  "editable": False,
                  "headerName": "Plan",
                  "cellStyle": { "backgroundColor": "silver" },
                },
                {
                  "field": f"{d.get('codigo')}-SISTEMA",
                  "editable": False,
                  "headerName": "Sistema",
                },
                {
                    "field": f"{d.get('codigo')}-CORREGIDO",
                    "editable": True,
                    "headerName": "Corr",
                },
                {
                    "field": f"{d.get('codigo')}-PROD",
                    "editable": False,
                    "headerName": "Prod",
                },
                {
                    "field": f"{d.get('codigo')}-VENTA",
                    "editable": False,
                    "headerName": "Venta",
                },
            ],
        })
    res.append(
        {
            "headerName": f"Anio {anio}",
            "children": children
        })

    return JsonResponse(res, safe=False)


def update_planificacion(data: []):
    for item in data:
        producto_id = item.get("id")
        for key, value in item.items():
            if key not in ('id'):
                codigo, op = key.split('-')
                fecha = datetime.strptime(f"{codigo}01", "%Y%m%d")
                prog = Planificacion.objects.get(producto_id=producto_id, fecha=fecha)
                if value == "":
                    value = None
                if op == 'PLAN':
                    prog.plan = value
                if op == 'SISTEMA':
                    prog.sistema = value
                if op == 'CORREGIDO':
                    prog.corregido = value
                if op == 'CORREGIDO':
                    prog.corregido = value
                prog.save()
    pass


def get_programacion(request, anio = 2025, mes = 7, responsable = None, semana = 0):
    condition = ""
    if responsable is not None and responsable != "Todos":
        condition = f" and pr.responsable = '{responsable}'"
    if semana is None:
        semana = 0

    sql = f"""
         select cp.producto_id as id,
                case when pr.nombre is null then cp.producto_nombre else pr.nombre end as producto_nombre,
                (select max(corregido) from costos_planificacion pl where pl.producto_id = cp.producto_id and  extract(year from pl.fecha) = extract(year from cp.fecha) and extract(month from pl.fecha) = extract(month from cp.fecha)) as planeado,
                pr.responsable,
                to_char(fecha, 'YYYYMMDD') as codigo,
                cp.plan,
                cp.prod
          from costos_programacion cp
            join costos_productos pr
              on pr.id = cp.producto_id
             and pr.habilitado = true
         where extract(year from fecha) = {anio}
           and extract(month from fecha) = {mes} 
           and (
            {semana} = 0
            or case 
                    when extract('week' from fecha) - extract('week' from '2024-{str(mes).rjust(2, "0")}-02'::date) + 1 < 0 then 5
                    else extract('week' from fecha) - extract('week' from '2024-{str(mes).rjust(2, "0")}-02'::date) + 1
               end = {semana}
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
    anio = int(request.GET.get("anio", "2025"))
    mes = int(request.GET.get("mes", "9"))
    semana = int(request.GET.get("semana", "0"))
    sql = f"""
        select distinct 
               case 
                    when extract('week' from fecha) - extract('week' from '2024-{str(mes).rjust(2, "0")}-02'::date) + 1 < 0 then 5
                    else extract('week' from fecha) - extract('week' from '2024-{str(mes).rjust(2, "0")}-02'::date) + 1
               end as semana,
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
         where extract(year from fecha) = {anio}
           and extract(month from fecha) = {mes}
           and (
            {semana} = 0
            or case 
                    when extract('week' from fecha) - extract('week' from '2024-{str(mes).rjust(2, "0")}-02'::date) + 1 < 0 then 5
                    else extract('week' from fecha) - extract('week' from '2024-{str(mes).rjust(2, "0")}-02'::date) + 1
               end = {semana}
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
    anio = int(request.GET.get("anio", 2025))
    mes = int(request.GET.get("mes", "9"))

    sql = f"""
    with prog as (select 
            pr.id,
            pr.ref_id,
            pr.nombre,
            pr.categoria,
            pr.responsable,
            sum(cp.prod) as prod,
            extract(month from cp.fecha) as mes,
            extract(year from cp.fecha) as anio
      from costos_programacion cp
        join costos_productos pr
          on pr.id = cp.producto_id
         and pr.habilitado = true
    where extract(year from cp.fecha) = {anio}
      and extract(month from cp.fecha) = {mes}
    group by pr.id, pr.ref_id, nombre, categoria, pr.responsable, extract(year from cp.fecha), extract(month from cp.fecha)),
    data as (select pr.nombre,
            pr.categoria,
            pr.responsable,
            (select max(plan) from costos_planificacion pl where pl.producto_id = pr.id and extract(year from fecha) = pr.anio and extract(month from fecha) = pr.mes) as plan,
            pr.prod,
            (select coalesce(sum(count), 0)
              from panacea_sales_v2 s
             where s.operation_year = pr.anio
               and s.operation_month = pr.mes
               and s.product_id = pr.id
            )::int vendido
      from prog pr)
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
    anio = int(request.GET.get("anio", 2025))
    mes = int(request.GET.get("mes", "9"))

    sql = f"""
    with prog as (select 
            pr.id,
            pr.ref_id,
            pr.nombre,
            pr.categoria,
            pr.responsable,
            sum(cp.prod) as prod,
            extract(month from cp.fecha) as mes,
            extract(year from cp.fecha) as anio
      from costos_programacion cp
        join costos_productos pr
          on pr.id = cp.producto_id
         and pr.habilitado = true
    where extract(year from cp.fecha) = {anio}
      and extract(month from cp.fecha) = {mes}
    group by pr.id, pr.ref_id, nombre, categoria, pr.responsable, extract(year from cp.fecha), extract(month from cp.fecha)),
    data as (select pr.nombre,
            pr.id,
            pr.mes,
            pr.categoria,
            pr.responsable,
            (select max(plan) from costos_planificacion pl where pl.producto_id = pr.id and extract(year from fecha) = pr.anio and extract(month from fecha) = pr.mes) as plan,
            pr.prod,
            (select coalesce(sum(count), 0)
              from panacea_sales_v2 s
             where s.operation_year = pr.anio
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
    anio = int(request.GET.get("anio", 2025))
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
                extract(year from cp.fecha) as anio,
                extract('week' from fecha) - extract('week' from '{str(anio)}-{str(mes).rjust(2, "0")}-02'::date) + 1 as semana
          from costos_programacion cp
            join costos_productos pr
              on pr.id = cp.producto_id
             and pr.habilitado = true
        where extract(year from cp.fecha) = {anio}
          and extract(month from cp.fecha) = {mes}
        group by cp.producto_id, pr.id, pr.ref_id, nombre, categoria, pr.responsable, extract(year from cp.fecha), extract(month from cp.fecha), semana),
        data as (select pr.producto_id,
                pr.nombre,
                pr.categoria,
                pr.responsable,
                (select max(corregido) from costos_planificacion pl where pl.producto_id = pr.id and extract(year from fecha) = pr.anio and extract(month from fecha) = pr.mes) as plan_mensual,
                pr.plan,
                pr.prod,
                mes,
                semana
          from prog pr)
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
                     and p.habilitado = true
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
                     and p.habilitado = true
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
