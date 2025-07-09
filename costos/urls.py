from django.urls import path, include
from django.http import JsonResponse
from . import views_old, statistics, views, apps, produccion, ventas

# Routers provide an easy way of automatically determining the URL conf.
from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter


class OptionalSlashRouter(SimpleRouter):
    """Make all trailing slashes optional in the URLs used by the viewsets
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = '/?'


def get_categories(request):
    return JsonResponse(["Materia Prima", "Honorarios", "Servicios", "Mantenimiento", "Delivery", "Impuestos"], safe=False)


router = OptionalSlashRouter()
router.register(r'insumos', views.InsumosViewSet)
router.register(r'productos', views.ProductosViewSet)
router.register(r'clientes', views.ClientesViewSet)
router.register(r'remitos', views.RemitosViewSet)
router.register(r'programacion', views.ProgramacionViewSet, basename="programacion")
router.register(r'planning', views.PlanificacionViewSet, basename="planning")
router.register(r'proveedores', views.ProveedorViewSet, basename="proveedores")
router.register(r'ctacteprov', views.CuentaCorrienteProveedorViewSet)

costos_router = NestedSimpleRouter(router, r'productos', lookup='producto')
costos_router.register(r'costos', views.CostosViewSet, basename='costos')

pagos_router = NestedSimpleRouter(router, r'ctacteprov', lookup='ctacteprov')
pagos_router.register(r'pagos', views.CuentaCorrienteProveedorPagosViewSet, basename='pagos')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(costos_router.urls)),
    path('costos_materia_prima', statistics.get_all_cost, name='get_all_cost', ),
    path('costos_materia_prima/<str:producto_id>', statistics.get_cost_by_product, name='get_cost_by_product'),
    path('products/<str:product_code>/history', statistics.get_product_history, name='get_product_history'),
    path('products/<str:product_code>/cronograma', statistics.get_product_cronograma, name='get_product_cronograma'),
    path('cronograma/<int:week_of_month>', statistics.get_cronograma_by_week_of_month, name='get_cronograma_by_week_of_month'),
    path('planning_columnas', produccion.get_planning_columns, name='planning_columnas'),
    path('programacion_columnas', produccion.get_programacion_columns, name='programacion_columnas'),
    path('categorias', get_categories),
    path('get_produccion_by_category', produccion.get_produccion_by_category, name='get_produccion_by_category'),
    path('get_produccion_by_productos', produccion.get_produccion_by_productos, name='get_produccion_by_productos'),
    path('precio_productos', statistics.get_precio_productos, name='precio_productos'),
    path('get_insumos_by_month', produccion.get_insumos_by_month, name='get_insumos_by_month'),
    path('get_ventas_por_cliente', ventas.get_ventas_por_cliente, name='get_ventas_por_cliente'),
]