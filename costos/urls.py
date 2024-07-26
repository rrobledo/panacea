from django.urls import path, include
from django.http import JsonResponse
from . import views, statistics, views_new, apps

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
router.register(r'insumos', views_new.InsumosViewSet)
router.register(r'productos', views_new.ProductosViewSet)
router.register(r'programacion', views_new.ProgramacionViewSet, basename="programacion")

costos_router = NestedSimpleRouter(router, r'productos', lookup='producto')
costos_router.register(r'costos', views_new.CostosViewSet, basename='costos')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(costos_router.urls)),
    path('costos_materia_prima', statistics.get_all_cost, name='get_all_cost', ),
    path('costos_materia_prima/<str:producto_id>', statistics.get_cost_by_product, name='get_cost_by_product'),
    path('planning_2024', statistics.get_planning_2024, name='get_planning_2024'),
    path('products/<str:product_code>/history', statistics.get_product_history, name='get_product_history'),
    path('products/<str:product_code>/cronograma', statistics.get_product_cronograma, name='get_product_cronograma'),
    path('cronograma/<int:week_of_month>', statistics.get_cronograma_by_week_of_month, name='get_cronograma_by_week_of_month'),
    path('planning', statistics.get_planning, name='get_planning'),
    path('categorias', get_categories),
]