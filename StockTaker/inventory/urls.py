from django.urls import path, re_path
from . import views

urlpatterns =  [
        path('',views.StockInstanceListView.as_view(),name='homepage'),
        re_path(r'^(?P<pk>\d+)$',views.StockInstanceDetailView.as_view(),name='stockInstance-detail'),
        path('create',views.StockInstanceCreate.as_view(),name='stockInstance-create'),
        re_path(r'^(?P<pk>\d+)/update/$',views.StockInstanceUpdate.as_view(),name='stockInstance-update'),
        re_path(r'^(?P<pk>\d+)/delete/$',views.StockInstanceDelete.as_view(),name='stockInstance-delete'),

]
