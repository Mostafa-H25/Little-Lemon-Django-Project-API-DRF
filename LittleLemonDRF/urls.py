from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path('api-token-auth', obtain_auth_token),
    path('groups/manager/users', views.ManagersView.as_view()),
    path('groups/manager/users/<int:pk>', views.DestroyManagersView.as_view()),
    path('groups/delivery-crew/users', views.DeliveyCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.DestroyDeliveryCrewView.as_view()),
    path('category', views.CategoryView.as_view()),
    path('category/<int:pk>', views.SingleCategoryView.as_view()),
    path('menu-items', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
]
