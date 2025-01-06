from django.db import connection
from django.http import JsonResponse
import itertools
from .models import Programacion, Productos
from datetime import datetime

def get_ventas_por_cliente(request):
    anio = int(request.GET.get("anio", 2025))
    mes = int(request.GET.get("mes", "9"))
    cliente = request.GET.get("cliente", "Todos")

    sql = f"""
        with aux as (select concat(
               date_part('YEAR', date(operation_date))::varchar,
               '-',
               lpad(date_part('MONTH', date(operation_date))::varchar, 2 , '0') ,
               '-',
               case
                   when extract(day from operation_date) between 1 and 7 then '1'
                   when extract(day from operation_date) between 8 and 15 then '2'
                   when extract(day from operation_date) between 16 and 23 then '3'
                   when extract(day from operation_date) between 24 and 31 then '4'
               end) as week_of_month,
               case 
                when customer_id = 999 then 'Panacea Carlos Paz'
                when customer_id = 0 then 'Panacea Villa Allende'
                else 'Dieteticas'
               end as cliente,
               sum(count) as cantidad, 
               sum(case when operation_hour between 8 and 15 then count else 0 end) as cantidad_maniana,
               sum(case when operation_hour between 15 and 21 then count else 0 end) as cantidad_tarde,
               sum(subtotal) as subtotal,
               sum(case when operation_hour between 8 and 15 then subtotal else 0 end) as subtotal_maniana,
               sum(case when operation_hour between 15 and 21 then subtotal else 0 end) as subtotal_tarde,
               count(distinct document_id) as count
           from panacea_sales
          where date_part('YEAR', date(operation_date)) = {anio}
            and ({mes} = 0 or date_part('MONTH', date(operation_date)) = {mes}) 
          group by 1, customer_id, customer
          ), 
        res as (
        select substring(week_of_month, 0, 8) as week_of_month,
               'TOTAL' as cliente,
               sum(cantidad)::int as cantidad,
               sum(cantidad_maniana)::int as cantidad_maniana,
               sum(cantidad_tarde)::int as cantidad_tarde,
               sum(subtotal) as subtotal,
               sum(subtotal_maniana) as subtotal_maniana,
               sum(subtotal_tarde) as subtotal_tarde
          from aux
         group by substring(week_of_month, 0, 8)
        union
        select substring(week_of_month, 0, 8) as week_of_month,
               concat('',cliente),
               sum(cantidad)::int as cantidad,
               sum(cantidad_maniana)::int as cantidad_maniana,
               sum(cantidad_tarde)::int as cantidad_tarde,
               sum(subtotal) as subtotal,
               sum(subtotal_maniana) as subtotal_maniana,
               sum(subtotal_tarde) as subtotal_tarde
          from aux
         group by substring(week_of_month, 0, 8), cliente
         union
         select week_of_month,
               'SUBTOTAL' as cliente,
               sum(cantidad)::int as cantidad,
               sum(cantidad_maniana)::int as cantidad_maniana,
               sum(cantidad_tarde)::int as cantidad_tarde,
               sum(subtotal) as subtotal,
               sum(subtotal_maniana) as subtotal_maniana,
               sum(subtotal_tarde) as subtotal_tarde
          from aux
         group by week_of_month
         union
         select week_of_month,
               concat(' ',cliente) as cliente,
               sum(cantidad)::int as cantidad,
               sum(cantidad_maniana)::int as cantidad_maniana,
               sum(cantidad_tarde)::int as cantidad_tarde,
               sum(subtotal) as subtotal,
               sum(subtotal_maniana) as subtotal_maniana,
               sum(subtotal_tarde) as subtotal_tarde
          from aux
         group by week_of_month, cliente
         order by week_of_month, subtotal desc)
        select week_of_month,
               cliente,
               cantidad_maniana,
               cantidad_tarde,
               cantidad,
               round(subtotal_maniana::decimal, 2) as subtotal_maniana,
               round(subtotal_tarde::decimal, 2) as subtotal_tarde,
               round(subtotal::decimal, 2) as subtotal
          from res
         where ('{cliente}' = 'Todos' or cliente = '{cliente}') 
         order by week_of_month, cliente desc
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
