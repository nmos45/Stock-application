from django.urls import path, re_path
from . import views

urlpatterns =  [
        path('',views.StockInstanceListView.as_view(),name='homepage'),
        re_path(r'^(?P<pk>\d+)$',views.StockInstanceDetailView.as_view(),name='stockInstance-detail'),
        path('create',views.StockInstanceCreate.as_view(),name='stockInstance-create'),
        re_path(r'^(?P<pk>\d+)/update/$',views.StockInstanceUpdate.as_view(),name='stockInstance-update'),
        re_path(r'^(?P<pk>\d+)/delete/$',views.StockInstanceDelete.as_view(),name='stockInstance-delete'),
        re_path(r'^stockfood/(?P<pk>\d+)/$',views.StockFoodDetail.as_view(),name='stockFood-detail'),
        re_path(r'^stockfood/create/(?P<pk>\d+)$',views.StockFoodCreate.as_view(),name='stockFood-create'),
        re_path(r'^stockfood/(?P<pk>\d+)/update/$',views.StockFoodUpdate.as_view(),name='stockFood-update'),
        re_path(r'^stockfood/(?P<pk>\d+)/delete/$',views.StockFoodDelete.as_view(),name='stockFood-delete'),
        path('foods',views.FoodListView.as_view(),name='all-foods'),
        re_path(r'^foods/(?P<pk>\d+)/$',views.FoodDetailView.as_view(),name='food-detail'),
        path('foods/create',views.FoodCreate.as_view(),name='food-create'),
        re_path(r'^foods/(?P<pk>\d+)/update/$',views.FoodUpdate.as_view(),name='food-update'),
]
