from rest_framework import serializers

from django.contrib.auth.models import User
from .models import Category, MenuItem, Cart, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id', 'username', 'email']
        extra_kwargs={
            'email':{'read_only':True},
        }


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    category=serializers.StringRelatedField()
    category_id=serializers.IntegerField(write_only=True)
    class Meta:
        model=MenuItem
        fields='__all__'
        

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields=['user','menuitem','quantity','unit_price', 'price']
        extra_kwargs={
            'user':{'read_only':True},
            'unit_price':{'read_only':True},
            'price':{'read_only':True},
        }


class UserOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=['id', 'user','total','delivery_crew','status', 'date']
        extra_kwargs={
            'user':{'read_only':True},
            'total':{'read_only':True},
            'date':{'read_only':True},
            'delivery_crew':{'read_only':True},
            'status':{'read_only':True},
        }
        
class DeliveryCrewOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=['id', 'user','total','delivery_crew','status', 'date']
        extra_kwargs={
            'user':{'read_only':True},
            'total':{'read_only':True},
            'date':{'read_only':True},
            'delivery_crew':{'read_only':True},
        }
        
class ManagerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=['id', 'user','total','delivery_crew','status', 'date']
        extra_kwargs={
            'user':{'read_only':True},
            'total':{'read_only':True},
            'date':{'read_only':True},
        }