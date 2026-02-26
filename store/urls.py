from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login_page'),
    path('logout/', views.logout_view, name='logout'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add_edit, name='product_add'),
    path('products/<int:pk>/edit/', views.product_add_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('orders/', views.order_list, name='order_list'),
]
