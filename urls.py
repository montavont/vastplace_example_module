from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

rest_patterns = [
    url(r'metal_rest', views.metal_rest, name='Metal rest'),
]

rest_patterns = format_suffix_patterns(rest_patterns)

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'tile_map', views.tile_map, name='Tile map'),
    url(r'cell_map', views.cell_map, name='Cell map'),
    url(r'metal_cdf', views.metal_cdf, name='Metal cdf'),
    url(r'metal_step', views.metal_step, name='Metal step'),
    url(r'metal_bar', views.metal_bar, name='Metal bar'),
] + rest_patterns

