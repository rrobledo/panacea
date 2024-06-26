from django.db import connection
from django.http import JsonResponse
from .models import Costs, CostsDetails
from vercel_app.settings import COSTO_TOTAL_FABRICA, TOTAL_HORAS_FABRICA_MENSUAL
import json
from functools import lru_cache


@lru_cache(3)
def get_cost_by_product(request, product_code):
    def gen_costs(d, recipe_count, total_cost):
        return {
            "supply_name": d.supply_code.name,
            "amount": d.amount * (recipe_count if d.type == 'V' else 1),
            "type": d.type,
            "individual_cost": round(d.supply_code.price / d.supply_code.measure * d.amount * (recipe_count if d.type == 'V' else 1), 2),
            "percentage_over_cost": round(d.supply_code.price / d.supply_code.measure * d.amount * (recipe_count if d.type == 'V' else 1) / total_cost * 100, 2),
        }

    cost = Costs.objects.get(product_code=product_code)
    cost_detail = CostsDetails.objects.filter(cost_code__code=cost.code).all()

    recipe_count = int(request.GET.get("recipe_count", None)) if request.GET.get("recipe_count", None) else 1
    units = (int(request.GET.get("units", None)) if request.GET.get("units", None) else cost.units) * recipe_count
    revenue = float(request.GET.get("revenue", None)) if request.GET.get("revenue", None) else cost.revenue
    current_price = float(request.GET.get("current_price", None)) if request.GET.get("current_price", None) else cost.current_price

    sum_cost = sum([d.supply_code.price / d.supply_code.measure * d.amount * (recipe_count if d.type == 'V' else 1) for d in cost_detail])
    suggested_price = round(sum_cost / units * ((revenue / 100) + 1), 2)
    costo_unitario_mp = round(sum_cost / units, 2)
    current_revenue = round(((current_price / sum_cost * units) - 1) * 100, 2)
    monthly_batches = int(TOTAL_HORAS_FABRICA_MENSUAL / cost.production_time)
    estimate_monthly_sales = round(units * monthly_batches * current_price, 2)
    estimate_monthly_cost = round(units * monthly_batches * costo_unitario_mp, 2)
    prod_revenue_monthly = round(estimate_monthly_sales - estimate_monthly_cost, 2)
    total_revenue_monthly = round(prod_revenue_monthly - COSTO_TOTAL_FABRICA, 2)
    revenue_monthly = round(((estimate_monthly_sales / (estimate_monthly_cost + COSTO_TOTAL_FABRICA)) - 1) * 100, 2)

    response = {
        "product_name": cost.product_code.name,
        "units": units,
        "revenue": revenue,
        "suggested_price": round(suggested_price, 2),
        "costo_unitario_mp": costo_unitario_mp,
        "costo_mp": round(costo_unitario_mp * units, 2),
        "current_price": current_price,
        "production_time": cost.production_time,
        "current_revenue": current_revenue,
        "utilidad_del_lote": round((current_price * units) - (costo_unitario_mp * units), 2),
        "current_sale_total": round(current_price * units, 2),
        "costo_unitario_total": round((costo_unitario_mp * units) / units, 2),
        "costo_total": round((costo_unitario_mp * units), 2),
        "venta_total": round(current_price * units, 2),
        "estimate_monthly_sales": estimate_monthly_sales,
        "estimate_monthly_cost": estimate_monthly_cost,
        "prod_revenue_monthly": prod_revenue_monthly,
        "total_revenue_monthly": total_revenue_monthly,
        "revenue_monthly": revenue_monthly,
        "cost_detail": sorted([gen_costs(d, recipe_count, sum_cost) for d in cost_detail], key=lambda x: x.get("percentage_over_cost"), reverse=True)
    }
    return JsonResponse(response)


def get_all_cost(request):
    costs = Costs.objects.all()
    prices = []
    for cost in costs:
        if cost.units > 1:
            ret = get_cost_by_product(request, cost.product_code)
            prod_cost = json.loads(ret.content)
            prod_cost.pop("cost_detail")
            prices.append({
                "product_code": cost.product_code.code,
                "product_name": prod_cost.get("product_name"),
                "units": prod_cost.get("units"),
                "current_price": prod_cost.get("current_price"),
                "costo_unitario_mp": prod_cost.get("costo_unitario_mp"),
                "costo_mp": prod_cost.get("costo_mp"),
                "costo_unitario_produccion": prod_cost.get("costo_unitario_produccion"),
                "costo_produccion": prod_cost.get("costo_produccion"),
                "suggested_price": prod_cost.get("suggested_price"),
                "costo_total": prod_cost.get("costo_total"),
                "costo_unitario_total": prod_cost.get("costo_unitario_total"),
                "venta_total": prod_cost.get("venta_total"),
                "current_revenue": prod_cost.get("current_revenue"),
                "production_time": prod_cost.get("production_time"),
                "estimate_monthly_sales": prod_cost.get("estimate_monthly_sales"),
                "estimate_monthly_cost": prod_cost.get("estimate_monthly_cost"),
                "prod_revenue_monthly": prod_cost.get("prod_revenue_monthly"),
                "total_revenue_monthly": prod_cost.get("total_revenue_monthly"),
                "revenue_monthly": prod_cost.get("revenue_monthly"),
                "utilidad_del_lote": prod_cost.get("utilidad_del_lote"),
            })
    prices = sorted(prices, key=lambda x: x.get("product_name"))
    return JsonResponse(prices, safe=False)


def get_product_history(request, product_code):
    def dictfetchall(cursor):
        """
        Return all rows from a cursor as a dict.
        Assume the column names are unique.
        """
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    sql_with_sales = """
        with sales as (select trim(coalesce(c.nombre, 'Otros')) as article,
               trim(a.nombre) as product,
               concat(
                date_part('year', d.fechadocumento),
                '-',
                to_char(date_part('month', d.fechadocumento), 'fm00'),
                case
                    when date_part('month', d.fechadocumento) = 1 then 'Ene'
                    when date_part('month', d.fechadocumento) = 2 then 'Feb'
                    when date_part('month', d.fechadocumento) = 3 then 'Mar'
                    when date_part('month', d.fechadocumento) = 4 then 'Abr'
                    when date_part('month', d.fechadocumento) = 5 then 'May'
                    when date_part('month', d.fechadocumento) = 6 then 'Jun'
                    when date_part('month', d.fechadocumento) = 7 then 'Jul'
                    when date_part('month', d.fechadocumento) = 8 then 'Ago'
                    when date_part('month', d.fechadocumento) = 9 then 'Oct'
                    when date_part('month', d.fechadocumento) = 10 then 'Sep'
                    when date_part('month', d.fechadocumento) = 11 then 'Nov'
                    when date_part('month', d.fechadocumento) = 12 then 'Dic'
                end
               ) as month_of_year,
               concat(
                date_part('year', d.fechadocumento),
                to_char(date_part('week', d.fechadocumento), 'fm00'),
                to_char(date_part('month', d.fechadocumento), 'fm00')
               ) as week_of_year_old,
               to_char(d.fechadocumento, 'YYYY-MM-DD') as operation_data,
               case 
                when a.nombre like '%x2%' then 2
                when a.nombre like '%x3%' then 3
                else 1
               end * dd.cantidad as total,
               dd.subtotal
          from documentos d 
            join documentosdetalles dd
              on d.iddocumento = dd.iddocumento 
            join articulos a 
              on dd.idarticulo = a.idarticulo 
            left outer join categorias c
              on a.idcategoria = c.idcategoria
       union select 'TOTAL' as article,
               'TOTAL' as product,
               concat(
                date_part('year', d.fechadocumento),
                '-',
                to_char(date_part('month', d.fechadocumento), 'fm00'),
                case
                    when date_part('month', d.fechadocumento) = 1 then 'Ene'
                    when date_part('month', d.fechadocumento) = 2 then 'Feb'
                    when date_part('month', d.fechadocumento) = 3 then 'Mar'
                    when date_part('month', d.fechadocumento) = 4 then 'Abr'
                    when date_part('month', d.fechadocumento) = 5 then 'May'
                    when date_part('month', d.fechadocumento) = 6 then 'Jun'
                    when date_part('month', d.fechadocumento) = 7 then 'Jul'
                    when date_part('month', d.fechadocumento) = 8 then 'Ago'
                    when date_part('month', d.fechadocumento) = 9 then 'Oct'
                    when date_part('month', d.fechadocumento) = 10 then 'Sep'
                    when date_part('month', d.fechadocumento) = 11 then 'Nov'
                    when date_part('month', d.fechadocumento) = 12 then 'Dic'
                end
               ) as month_of_year,
               concat(
                date_part('year', d.fechadocumento),
                to_char(date_part('week', d.fechadocumento), 'fm00'),
                to_char(date_part('month', d.fechadocumento), 'fm00')
               ) as week_of_year_old,
               to_char(d.fechadocumento, 'YYYY-MM-DD') as operation_data,
               case 
                when a.nombre like '%x2%' then 2
                when a.nombre like '%x3%' then 3
                else 1
               end * dd.cantidad as total,
               dd.subtotal
          from documentos d 
            join documentosdetalles dd
              on d.iddocumento = dd.iddocumento 
            join articulos a 
              on dd.idarticulo = a.idarticulo 
            left outer join categorias c
              on a.idcategoria = c.idcategoria)
    """
    sql_products = f"""
        {sql_with_sales}
        select distinct article
          from sales
         order by 1;
    """

    sql_months = f"""
        {sql_with_sales}
        select distinct month_of_year
          from sales
         order by 1;
    """

    sql_data = f"""
        {sql_with_sales}
        select article || '-' || month_of_year as key,
               sum(total) as total,
               sum(subtotal) as sub_total
          from sales
         where article = '{product_code}'          
         group by article, month_of_year
         order by 1;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql_products)
        products = dictfetchall(cursor)

    with connection.cursor() as cursor:
        cursor.execute(sql_months)
        months = dictfetchall(cursor)

    with connection.cursor() as cursor:
        cursor.execute(sql_data)
        data = dictfetchall(cursor)

    items = zip(products, months)

    r1 = {}
    for d in data:
        r1[d.get("key")] = d.get("total")

    series = []
    for p in [{"article": product_code}]:
        p_data = []
        for m in months:
            key = f'{p.get("article")}-{m.get("month_of_year")}'
            p_data.append(r1.get(key, 0))
        series.append({
            "name": p.get("article"),
            "data": p_data
        })

    categories = [m.get("month_of_year") for m in months]
    return JsonResponse({
        "products": [{"value": p.get("article"), "label":  p.get("article")} for p in products],
        "series": series,
        "categories": categories
    }, safe=False)


def get_product_cronograma(request, product_code):

    sql_with_sales = """
        with sales as (select c.nombre as article,
                case 
	    	        when d.idcliente = 0 then 'Local'
	    	        else 'Dietetica'
                end as lugar_venta,
               concat(
                case 
                	when extract(isodow from d.fechadocumento) = 1 then '01 Lunes' 
                	when extract(isodow from d.fechadocumento) = 2 then '02 Martes'
                	when extract(isodow from d.fechadocumento) = 3 then '03 Miercoles'
                	when extract(isodow from d.fechadocumento) = 4 then '04 Jueves'
                	when extract(isodow from d.fechadocumento) = 5 then '05 viernes'
                	when extract(isodow from d.fechadocumento) = 6 then '06 Sabado'
                	when extract(isodow from d.fechadocumento) = 7 then '01 Lunes'
                end
               ) as serie,
               to_char(d.fechadocumento, 'YYYY-MM-DD') as operation_data,
               sum(case 
                when a.nombre like '%x2%' then 2
                when a.nombre like '%x3%' then 3
                else 1
               end * dd.cantidad) as total,
               sum(dd.subtotal) as subtotal
          from documentos d 
            join documentosdetalles dd
              on d.iddocumento = dd.iddocumento 
            join articulos a 
              on dd.idarticulo = a.idarticulo   
            join categorias c
              on a.idcategoria = c.idcategoria
         where d.fechadocumento > CURRENT_DATE - INTERVAL '2 months'
           group by 1, 2, 4, 3)
    """
    sql_products = f"""
        {sql_with_sales}
        select distinct article
          from sales
         order by 1;
    """

    sql_months = f"""
        {sql_with_sales}
        select distinct serie
          from sales
         order by 1;
    """

    sql_data = f"""
        {sql_with_sales}
        select lugar_venta || article || '-' || serie as key,
               avg(total)::int as total,
               avg(subtotal) as sub_total
          from sales
         where article = '{product_code}'          
         group by lugar_venta, article, serie
         order by 1;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql_products)
        products = _dictfetchall(cursor)

    with connection.cursor() as cursor:
        cursor.execute(sql_months)
        months = _dictfetchall(cursor)

    with connection.cursor() as cursor:
        cursor.execute(sql_data)
        data = _dictfetchall(cursor)

    items = zip(products, months)

    r1 = {}
    for d in data:
        r1[d.get("key")] = d.get("total")

    series = []
    # for p in [{"article": f"Dietetica{product_code}"}, {"article": f"Local{product_code}"}]:
    #     p_data = []
    #     for m in months:
    #         key = f'{p.get("article")}-{m.get("serie")}'
    #         p_data.append(r1.get(key, 0))
    #     series.append({
    #         "name": p.get("article"),
    #         "data": p_data
    #     })

    for p in [{"article": f"{product_code}"}]:
        p_data = []
        for m in months:
            key = f'Dietetica{p.get("article")}-{m.get("serie")}'
            p_data.append(r1.get(key, 0))
        series.append({
            "name": f"Dietetica{p.get('article')}",
            "data": p_data
        })
        p_data = []
        for m in months:
            key = f'Local{p.get("article")}-{m.get("serie")}'
            p_data.append(r1.get(key, 0))
        series.append({
            "name": f"Local{p.get('article')}",
            "data": p_data
        })
        p_data = []
        for m in months:
            keyDietetica = f'Dietetica{p.get("article")}-{m.get("serie")}'
            keyLocal = f'Local{p.get("article")}-{m.get("serie")}'
            p_data.append(r1.get(keyDietetica, 0) + r1.get(keyLocal, 0))
        series.append({
            "name": f"Total{p.get('article')}",
            "data": p_data
        })


    categories = [m.get("serie") for m in months]
    return JsonResponse({
        "products": [{"value": p.get("article"), "label":  p.get("article")} for p in products],
        "series": series,
        "categories": categories
    }, safe=False)


def get_cronograma_by_week_of_month(request, week_of_month):
    sql = f"""
        with sales as (select c.nombre as article,
               case 
                   when a.nombre in ('Facturas', 'Facturas x2') then 'Facturas' 
                   when a.nombre in ('Medialunas', 'Medialunas x2') then 'Medialunas'
                   else a.nombre 
               end as product,
                case 
                    when d.idcliente = 0 then 'Local'
                    else 'Dietetica'
                end as lugar_venta,
               case
                   when extract(day from d.fechadocumento) between 1 and 7 then 1
                   when extract(day from d.fechadocumento) between 8 and 15 then 2
                   when extract(day from d.fechadocumento) between 16 and 23 then 3
                   when extract(day from d.fechadocumento) between 24 and 31 then 4
               end as week_of_month,
               concat(
                case 
                    when extract(isodow from d.fechadocumento) = 1 then '01 Lunes' 
                    when extract(isodow from d.fechadocumento) = 2 then '02 Martes'
                    when extract(isodow from d.fechadocumento) = 3 then '03 Miercoles'
                    when extract(isodow from d.fechadocumento) = 4 then '04 Jueves'
                    when extract(isodow from d.fechadocumento) = 5 then '05 Viernes'
                    when extract(isodow from d.fechadocumento) = 6 then '06 Sabado'
                    when extract(isodow from d.fechadocumento) = 7 then '01 Lunes'
                end
               ) as serie,
               to_char(d.fechadocumento, 'YYYY-MM-DD') as operation_date,
               sum(case 
                when a.nombre like '%x2%' then 2
                when a.nombre like '%x3%' then 3
                else 1
               end * dd.cantidad) as total,
               sum(dd.subtotal) as subtotal
          from documentos d 
            join documentosdetalles dd
              on d.iddocumento = dd.iddocumento 
            join articulos a 
              on dd.idarticulo = a.idarticulo   
            join categorias c
              on a.idcategoria = c.idcategoria
         where d.fechadocumento > CURRENT_DATE - INTERVAL '2 months'
            and case
                   when extract(day from d.fechadocumento) between 1 and 7 then 1
                   when extract(day from d.fechadocumento) between 8 and 15 then 2
                   when extract(day from d.fechadocumento) between 16 and 23 then 3
                   when extract(day from d.fechadocumento) between 24 and 31 then 4
               end = {week_of_month} 
           group by article, product, lugar_venta, week_of_month, serie, operation_date),
        --join_1 as (select distinct article, product from pre_sales),
        --join_2 as (select * from (values ('Dietetica'), ('Local')) as t(lugar_venta)),
        --join_3 as (select distinct week_of_month, serie, operation_date  from pre_sales),
        --keys as (select * from join_1, join_2, join_3),
        --sales2 as (
        -- select k.article,
        -- 	    k.product,
        -- 	    k.lugar_venta,
        -- 	    k.week_of_month,
        -- 	    k.serie,
        -- 	    k.operation_date,
        -- 	    coalesce(p.total, 0) as total,
        -- 	    coalesce(p.subtotal, 0) as subtotal
        --   from keys k
        --   	left outer join pre_sales p
        --   	  on k.article = p.article
        --   	 and k.product = p.product
        --   	 and k.lugar_venta = p.lugar_venta
        --   	 and k.operation_date = p.operation_date
        --),
        values as (select distinct week_of_month,
               article,
               product
          from sales
         order by 1),
        report as (select week_of_month, 
                product,
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month 
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Dietetica'
                   and s.serie = '01 Lunes') as lunes_dietetica,
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Local'
                   and s.serie = '01 Lunes') as lunes_local,
               ----   MARTES ----
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Dietetica'
                   and s.serie = '02 Martes') as martes_dietetica,
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Local'
                   and s.serie = '02 Martes') as martes_local,
               ----   MIERCOLES ----
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Dietetica'
                   and s.serie = '03 Miercoles') as miercoles_dietetica,
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Local'
                   and s.serie = '03 Miercoles') as miercoles_local,
               ----   JUEVES ----
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Dietetica'
                   and s.serie = '04 Jueves') as jueves_dietetica,
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Local'
                   and s.serie = '04 Jueves') as jueves_local,
               ----   VIERNES ----
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Dietetica'
                   and s.serie = '05 Viernes') as viernes_dietetica,
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Local'
                   and s.serie = '05 Viernes') as viernes_local,
               ----   SABADO ----
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Dietetica'
                   and s.serie = '06 Sabado') as sabado_dietetica,
               (select coalesce(avg(s.total)::int, 0)
                  from sales s
                 where s.week_of_month = v.week_of_month
                   and s.article = v.article
                   and s.product = s.product
                   and s.lugar_venta = 'Local'
                   and s.serie = '06 Sabado') as sabado_local
          from values v)
        select week_of_month,
               product,
               lunes_dietetica,
               lunes_local,
               lunes_dietetica + lunes_local as lunes,
               martes_dietetica,
               martes_local,
               martes_dietetica + martes_local as martes,
               miercoles_dietetica,
               miercoles_local,
               miercoles_dietetica + miercoles_local as miercoles, 
               jueves_dietetica,
               jueves_local,
               jueves_dietetica + jueves_local as jueves, 
               viernes_dietetica,
               viernes_local,
               viernes_dietetica + viernes_local as viernes, 
               sabado_dietetica,
               sabado_local,
               sabado_dietetica + sabado_local as sabado,
               lunes_dietetica + martes_dietetica + miercoles_dietetica + jueves_dietetica + viernes_dietetica + sabado_dietetica  as total_semanal_dietetica,
               lunes_local + martes_local + miercoles_local + jueves_local + viernes_local + sabado_local as total_semanal_local,
               lunes_dietetica + lunes_local + martes_dietetica + martes_local + miercoles_dietetica + miercoles_local + jueves_dietetica + jueves_local + viernes_dietetica + viernes_local + sabado_dietetica + sabado_local as total_semanal        
          from report
        order by product, week_of_month    
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = _dictfetchall(cursor)

    return JsonResponse(result, safe=False)


def get_planning(request):

    sql_planning = """
        with sales as (select 
               case 
                   when a.nombre in ('Facturas', 'Facturas x2', 'Medialunas', 'Medialunas x2') then 106 
                   else a.idarticulo 
               end as product_id,
               c.nombre as article,
               case 
                   when a.nombre in ('Facturas', 'Facturas x2', 'Medialunas', 'Medialunas x2') then 'Facturas-Medialunas' 
                   else a.nombre 
               end as product,
               case 
                   when d.idcliente = 0 then 'Local'
                   else 'Dietetica'
               end as lugar_venta,
               concat(
                date_part('year', d.fechadocumento),
                '-',
                to_char(date_part('month', d.fechadocumento), 'fm00'),
                case
                    when date_part('month', d.fechadocumento) = 1 then 'Ene'
                    when date_part('month', d.fechadocumento) = 2 then 'Feb'
                    when date_part('month', d.fechadocumento) = 3 then 'Mar'
                    when date_part('month', d.fechadocumento) = 4 then 'Abr'
                    when date_part('month', d.fechadocumento) = 5 then 'May'
                    when date_part('month', d.fechadocumento) = 6 then 'Jun'
                    when date_part('month', d.fechadocumento) = 7 then 'Jul'
                    when date_part('month', d.fechadocumento) = 8 then 'Ago'
                    when date_part('month', d.fechadocumento) = 9 then 'Sep'
                    when date_part('month', d.fechadocumento) = 10 then 'Oct'
                    when date_part('month', d.fechadocumento) = 11 then 'Nov'
                    when date_part('month', d.fechadocumento) = 12 then 'Dic'
                end
               ) as month_of_year,
               concat(
                date_part('year', d.fechadocumento),
                to_char(date_part('week', d.fechadocumento), 'fm00'),
                to_char(date_part('month', d.fechadocumento), 'fm00')
               ) as week_of_year_old,
               to_char(d.fechadocumento, 'YYYY-MM-DD') as operation_data,
               case 
                when a.nombre like '%x2%' then 2
                when a.nombre like '%x3%' then 3
                else 1
               end * dd.cantidad as total,
               dd.subtotal
          from documentos d 
            join documentosdetalles dd
              on d.iddocumento = dd.iddocumento 
            join articulos a 
              on dd.idarticulo = a.idarticulo
            join categorias c
              on a.idcategoria = c.idcategoria),
        planning as (
        select p.codigo as product_id, 
               p.productos as product_name, 
               unnest(array['2024','2024','2024','2024','2024','2024','2024','2024','2024','2024','2024','2024']) as year,
               unnest(array['Enero', 'Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']) as month,
               unnest(array[jan2024, feb2024,mar2024,apr2024,may2024,jun2024,jul2024,aug2024,sep2024,oct2024,nov2024,dec2024]) as total
          from planificacion2024 p 
         where p.productos not in ('Total unidades')),
        total as (
        select p.product_id,
                cp.code as product_code,
                p.product_name, 
                year, 
                month, 
                total,
                case 
                    when a.noaplicardescuento = 1
                        then case
                                when p.product_name like '%100gr%'
                                    then a.ubicacion::int / 10
                                else a.ubicacion::int
                        end
                    else a.preciopublico
                end as precio, 
                total * case 
                    when a.noaplicardescuento = 1
                        then case
                                when p.product_name like '%100gr%'
                                    then a.ubicacion::int / 10
                                else a.ubicacion::int
                        end
                    else a.preciopublico
                end as total_venta
          from planning p
            left outer join articulos a 
              on p.product_id = a.idarticulo
            left outer join costos_products cp 
              on cp.ref_id::int = p.product_id),
        subtotal as (
              select *,
         (select sum(total)
          from sales
         where month_of_year = '2024-03Mar'
           and product_id = total.product_id
         ) total_actual,
         (select sum(total)
          from sales
         where month_of_year = '2024-03Mar'
           and product_id = total.product_id
         ) * precio as total_venta_actual
          from total
         where month = 'Marzo')
        select *
          from subtotal
         where month = 'Marzo'
         order by product_name    
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_planning)
        planning = _dictfetchall(cursor)

    for prod in planning:
        try:
            prod.pop("total_venta")
            prod["precio"] = int(int(prod["precio"] if prod["precio"] is not None else 0) * 0.80)
            prod["total_venta_actual"] = 0

            if prod.get("product_code"):
                ret = get_cost_by_product(request, prod.get("product_code"))
                prod_cost = json.loads(ret.content)
                prod["total_actual"] = prod["total_actual"] if prod["total_actual"] is not None else 0
                prod["precio"] = prod_cost.get("current_price")
                prod["costo_unitario_mp"] = prod_cost.get("costo_unitario_mp")
                prod["costo_mp"] = prod_cost.get("costo_mp")
                prod["costo_unitario_produccion"] = prod_cost.get("costo_unitario_produccion")
                prod["costo_produccion"] = prod_cost.get("costo_produccion")
                prod["costo_total"] = prod_cost.get("costo_total")
                prod["costo_unitario_total"] = prod_cost.get("costo_unitario_total")
                prod["costo_total_planeado"] = prod.get("costo_unitario_total") * prod.get("total")
                prod["costo_total_actual"] = prod.get("costo_unitario_total", 0) * prod.get("total_actual", 0)
                prod["total_venta_planeado"] = prod.get("precio", 0) * prod.get("total", 0)
                prod["total_venta_actual"] = prod.get("precio", 0) * prod.get("total_actual", 0)
                prod["ganancia_planeado"] = prod["total_venta_planeado"] - prod["costo_total_planeado"]
                prod["ganancia_actual"] = prod["total_venta_actual"] - prod["costo_total_actual"]
                prod["porcentaje_ganancia_prod"] = round((prod.get("precio", 0) / prod.get("costo_unitario_total", 1) - 1) * 100, 2)
            pass
        finally:
            pass

    total = sum([int(d.get("total", 0)) for d in planning])
    total_actual = sum([int(d.get("total_actual", 0)) if d.get("total_actual") != '' and d.get("total_actual") is not None else 0 for d in planning])
    total_venta_planeado = round(sum([float(d.get("total_venta_planeado", 0)) if d.get("total_venta_planeado") != '' and d.get("total_venta_planeado") is not None else 0 for d in planning]), 2)
    total_venta_actual = round(sum([float(d.get("total_venta_actual", 0)) if d.get("total_venta_actual") != '' and d.get("total_venta_actual") is not None else 0 for d in planning]), 2)
    costo_total_planeado = round(sum([float(d.get("costo_total_planeado", 0)) if d.get("costo_total_planeado") != '' and d.get("costo_total_planeado") is not None else 0 for d in planning]), 2)
    costo_total_actual = round(sum([float(d.get("costo_total_actual", 0)) if d.get("costo_total_actual") != '' and d.get("costo_total_actual") is not None else 0 for d in planning]), 2)
    ganancia_planeado = total_venta_planeado - costo_total_planeado
    ganancia_actual = total_venta_actual - costo_total_actual
    porcentaje_ganancia_prod = round(sum([float(d.get("porcentaje_ganancia_prod", 0)) if d.get("porcentaje_ganancia_prod") != '' and d.get("porcentaje_ganancia_prod") is not None else 0 for d in planning]) / sum([1 if d.get("porcentaje_ganancia_prod") != '' and d.get("porcentaje_ganancia_prod") is not None else 0 for d in planning]), 2)

    planning.append(
        {
            "product_id": 0,
            "product_code": "TOTALES",
            "product_name": "TOTALES",
            "year": "2024",
            "month": "Enero",
            "total": total,
            "precio": 0,
            "total_actual": total_actual,
            "total_venta_actual": total_venta_actual,
            "total_venta_planeado": total_venta_planeado,
            "costo_producto": 0,
            "costo_total_planeado": costo_total_planeado,
            "costo_total_actual": costo_total_actual,
            "ganancia_planeado": ganancia_planeado,
            "ganancia_actual": ganancia_actual,
            "porcentaje_ganancia_prod": porcentaje_ganancia_prod,
        })

    return JsonResponse(planning, safe=False)


def _dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
