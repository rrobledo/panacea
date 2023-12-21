from django.urls import path, include
from rest_framework import routers
from . import views, statistics

# Routers provide an easy way of automatically determining the URL conf.
#router = routers.DefaultRouter()
from rest_framework.routers import DefaultRouter

class OptionalSlashRouter(DefaultRouter):
    """Make all trailing slashes optional in the URLs used by the viewsets
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = '/?'


router = OptionalSlashRouter()
router.register(r'supplies', views.SuppliesViewSet)
router.register(r'products', views.ProductsViewSet)
router.register(r'costs', views.CostsViewSet)
router.register(r'costs_details', views.CostsDetailsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reports/prices', statistics.get_all_cost, name='get_all_cost'),
    path('products/<str:product_code>/cost', statistics.get_cost_by_product, name='get_cost_by_product'),
    path('products/<str:product_code>/history', statistics.get_product_history, name='get_product_history'),
    path('products/<str:product_code>/cronograma', statistics.get_product_cronograma, name='get_product_cronograma'),
]