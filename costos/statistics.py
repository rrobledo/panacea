from django.db import connection
from django.http import JsonResponse
from .models import Costs, CostsDetails
import json


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
    data = CostsDetails.objects.filter(cost_code__code=cost.code).all()

    recipe_count = int(request.GET.get("recipe_count", None)) if request.GET.get("recipe_count", None) else 1
    units = (int(request.GET.get("units", None)) if request.GET.get("units", None) else cost.units) * recipe_count
    revenue = float(request.GET.get("revenue", None)) if request.GET.get("revenue", None) else cost.revenue
    current_price = float(request.GET.get("current_price", None)) if request.GET.get("current_price", None) else cost.current_price

    sum_cost = sum([d.supply_code.price / d.supply_code.measure * d.amount * (recipe_count if d.type == 'V' else 1) for d in data])
    suggested_price = round(sum_cost / units * ((revenue / 100) + 1), 2)
    current_revenue = round(((current_price / sum_cost * units) - 1) * 100, 2)
    response = {
        "product_name": cost.product_code.name,
        "units": units,
        "revenue": revenue,
        "suggested_price": suggested_price,
        "current_price": current_price,
        "current_revenue": current_revenue,
        "current_sale_total": round(current_price * units, 2),
        "cost_total": round(sum_cost, 2),
        "sale_total": round(suggested_price * units, 2),
        "cost_detail": [gen_costs(d, recipe_count, sum_cost) for d in data]
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
                "suggested_price": prod_cost.get("suggested_price"),
                "cost_total": prod_cost.get("cost_total"),
                "sale_total": prod_cost.get("sale_total")
            })
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
        with sales as (select c.nombre as article,
               a.nombre as product,
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
            join categorias c
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
    def dictfetchall(cursor):
        """
        Return all rows from a cursor as a dict.
        Assume the column names are unique.
        """
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

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
         where d.fechadocumento > CURRENT_DATE - INTERVAL '4 months'
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

