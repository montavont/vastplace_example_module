from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

rest_patterns = [
]

rest_patterns = format_suffix_patterns(rest_patterns)


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'tile_map', views.tile_map, name='Tile map'),
    url(r'cell_map', views.cell_map, name='Cell map'),
] + rest_patterns

