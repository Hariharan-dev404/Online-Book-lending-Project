from rest_framework import serializers
from .models import Book, Order, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'created_at']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    book_details = BookSerializer(source='book', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
