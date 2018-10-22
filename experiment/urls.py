from django.conf.urls import url, include
from . import views


image_patterns = [
    url(r'^$', views.ImageListView.as_view(), name='image-index'),
    url(r'^create$', views.ImageCreateView.as_view(), name='image-create'),
]

urlpatterns = [
    url(r'^$', views.ExperimentListView.as_view()),
    url(r'^create$', views.ExperimentCreateView.as_view(), name='experiment-create'),
    url(r'^view/(?P<pk>[0-9]+)/$', views.ExperimentDetailView.as_view(), name='experiment-detail'),
    url(r'^view/(?P<pk>[0-9]+)/start$', views.start_experiment, name='experiment-start'),
    url(r'^view/(?P<pk>[0-9]+)/stop$', views.stop_experiment, name='experiment-stop'),
    url(r'^view/(?P<pk>[0-9]+)/scale$', views.scale_experiment, name='experiment-scale'),
    url(r'^image/', include(image_patterns)),
]
