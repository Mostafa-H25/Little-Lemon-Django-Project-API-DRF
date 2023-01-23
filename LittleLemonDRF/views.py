from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser, IsAuthenticated
from rest_framework.exceptions import NotFound, MethodNotAllowed

from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import UserSerializer, CategorySerializer, MenuItemSerializer, CartSerializer, UserOrderSerializer, DeliveryCrewOrderSerializer, ManagerOrderSerializer


class CategoryView(generics.ListCreateAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[DjangoModelPermissions]
    
    # def perform_create(self, serializer):
    #     if  not self.request.user.groups.filter(name='Manager').exists():
    #         raise PermissionDenied()
    #     else:
    #         serializer.save()
            

class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [DjangoModelPermissions]

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    permission_classes = [DjangoModelPermissions]
    
    ordering_fields = ['category','price']
    filterset_fields = ['category', 'featured']
    search_fields = ['title', 'category__title']
    
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [DjangoModelPermissions]

    
class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user.id)
    
    def perform_create(self, serializer):
        featured = MenuItem.objects.filter(title=serializer.validated_data['menuitem']).values_list('featured')[0][0]
        if featured: 
            data = {}
            data['user'] = self.request.user
            data['menuitem'] = serializer.validated_data['menuitem']
            data['quantity'] = serializer.validated_data['quantity']
            data['unit_price'] = MenuItem.objects.filter(title=data['menuitem']).values_list('price')[0][0]
            data['price'] = data['quantity']*data['unit_price']
            if serializer.is_valid():
                serializer.save(**data)
        else:
            raise NotFound('This item is not available in the store at the moment.', 404)
        
    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user=self.request.user).delete()
        return Response("Items in cart has been deleted", status=status.HTTP_200_OK)


class OrderView(generics.ListCreateAPIView):
    serializer_class = UserOrderSerializer
    permission_classes = [DjangoModelPermissions]    
    
    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=self.request.user)
        else:
            return Order.objects.filter(user=self.request.user.id)
    
    def perform_create(self, serializer):
        data = {}
        data['user'] = self.request.user
        data['total'] = 0
        order_items = []
        cart = Cart.objects.filter(user=self.request.user).values()
        for item in cart:
            data['total'] += item['price'] 
            menuitem_inst = MenuItem.objects.get(pk=item['menuitem_id'])
            OrderItem.objects.create(
                order = self.request.user,
                menuitem = menuitem_inst,
                quantity = item['quantity'],
                unit_price = item['unit_price'], 
                price = item['price']
            )
        if serializer.is_valid():
            serializer.save(**data)
            Cart.objects.filter(user=self.request.user).delete()
        
        
class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserOrderSerializer
    permission_classes = [IsAuthenticated]    
    
    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=self.request.user.id)
        else:
            return Order.objects.filter(user=self.request.user.id)
    
    def get_serializer_class(self):
        if self.request.user.groups.filter(name='Manager').exists():
            return ManagerOrderSerializer
        elif self.request.user.groups.filter(name='Delivery Crew').exists():
            return DeliveryCrewOrderSerializer
        else:
            return UserOrderSerializer
    
    def perform_update(self, serializer):
        member= serializer.validated_data['delivery_crew']
        delivery_crew = User.objects.filter(username=member).values_list('groups')[0][0]
        if delivery_crew == 2: 
            instance = self.get_object()
            data = self.request.data
            serializer = self.get_serializer(instance, data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
        else:
            raise NotFound('This user is not staff.', 404)
    
    def perform_destroy(self,instance):
        if not self.request.user.groups.filter(name='Manager').exists():
            raise MethodNotAllowed('Delete',"Order can't be deleted. Order has already been shipped.", code=403)
        else:
            instance.delete()
            return Response('Order has been deleted.', status=status.HTTP_204_NO_CONTENT)












class ManagersView(generics.ListCreateAPIView):
    serializer_class=UserSerializer
    
    def get_queryset(self):
        if not self.request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to access managers data associated with Little Lemon Resturant.")
        return User.objects.filter(groups__name='Manager')
    
    def perform_create(self, serializer):
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Manager')
        managers.user_set.add(user)
        return Response(status.HTTP_201_CREATED)


class DestroyManagersView(generics.RetrieveDestroyAPIView):
    queryset=User.objects.all()
    serializer_class=UserSerializer
    
    def get_queryset(self):
        if not self.request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to access managers data associated with Little Lemon Resturant.")
        return User.objects.filter(groups__name='Manager')
    
    def perform_destroy(self, instance):
        user = get_object_or_404(User, username=instance)
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({'message':'User has been successfully removed from manager position.'},status.HTTP_200_OK)


class DeliveyCrewView(generics.ListCreateAPIView):
    queryset=User.objects.all()
    serializer_class=UserSerializer
    
    def get_queryset(self):
        if not self.request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to access managers data associated with Little Lemon Resturant.")
        return User.objects.filter(groups__name='Delivery Crew')
    
    def perform_create(self, serializer):
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        delivery_crew = Group.objects.get(name='Delivery Crew')
        delivery_crew.user_set.add(user)
        return Response(status.HTTP_201_CREATED)


class DestroyDeliveryCrewView(generics.RetrieveDestroyAPIView):
    queryset=User.objects.all()
    serializer_class=UserSerializer
    
    def get_queryset(self):
        if not self.request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to access managers data associated with Little Lemon Resturant.")
        return User.objects.filter(groups__name='Delivery Crew')
    
    def perform_destroy(self, instance):
        user = get_object_or_404(User, username=instance)
        delivery_crew = Group.objects.get(name='Delivery Crew')
        delivery_crew.user_set.remove(user)
        return Response({'message':'User has been successfully removed from manager position.'},status.HTTP_200_OK)



