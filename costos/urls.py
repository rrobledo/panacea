from django.urls import path, include
from django.http import JsonResponse
from rest_framework import routers
from . import views, statistics

# Routers provide an easy way of automatically determining the URL conf.
#router = routers.DefaultRouter()
from rest_framework.routers import DefaultRouter
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
# router.register(r'supplies', views.SuppliesViewSet)
router.register(r'insumos', views.SuppliesViewSet)
# router.register(r'products', views.ProductsViewSet)
router.register(r'productos', views.ProductsViewSet)
# router.register(r'costs', views.CostsViewSet)
router.register(r'costos', views.CostsViewSet)
router.register(r'gastos', views.ComprasViewSet)
# router.register(r'costos/<str:code_cost>/cost_detail', views.CostsDetailsViewSet, basename='CostsDetailsViewSet')
costos_router = NestedSimpleRouter(router, r'costos', lookup='costo')
costos_router.register(r'costos_detail', views.CostsDetailsViewSet, basename='costos_detail')
# router.register(r'costs_details', views.CostsDetailsViewSet, basename='CostsDetailsViewSet')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(costos_router.urls)),
    # path('reports/prices', statistics.get_all_cost, name='get_all_cost', ),
    path('costos_materia_prima', statistics.get_all_cost, name='get_all_cost', ),
    path('costos_materia_prima/<str:product_code>', statistics.get_cost_by_product, name='get_cost_by_product'),
    # path('products/<str:product_code>/cost', statistics.get_cost_by_product, name='get_cost_by_product'),
    path('products/<str:product_code>/history', statistics.get_product_history, name='get_product_history'),
    path('products/<str:product_code>/cronograma', statistics.get_product_cronograma, name='get_product_cronograma'),
    path('cronograma/<int:week_of_month>', statistics.get_cronograma_by_week_of_month, name='get_cronograma_by_week_of_month'),
    path('planning', statistics.get_planning, name='get_planning'),
    path('categorias', get_categories),
]