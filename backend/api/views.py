from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from .models import Book, Order, User
from .serializers import BookSerializer, OrderSerializer, UserSerializer
import razorpay
from django.conf import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['POST'])
def create_razorpay_order(request):
    try:
        data = request.data
        order_id = data.get('order_id')
        order = Order.objects.get(id=order_id)
        
        # Razorpay takes amount in paise (1 INR = 100 paise)
        amount = int(order.book.price * 100)
        
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": f"receipt_{order.id}"
        })
        
        # Save razorpay order id
        order.razorpay_order_id = razorpay_order['id']
        order.save()
        
        return Response(razorpay_order, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except razorpay.errors.BadRequestError as e:
        return Response({"error": "Razorpay API key is invalid or not configured. Please add your real Test Key to settings.py."}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({"error": f"Payment gateway error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def verify_payment(request):
    try:
        data = request.data
        params_dict = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }
        
        # Verify signature
        client.utility.verify_payment_signature(params_dict)

        # Payment signature verified successfully
        order = Order.objects.get(razorpay_order_id=data.get('razorpay_order_id'))
        order.payment_status = 'success'
        order.razorpay_payment_id = data.get('razorpay_payment_id')
        
        # Reduce stock logic
        book = order.book
        if book.stock > 0:
            book.stock -= 1
            if book.stock == 0:
                book.status = 'sold'
            book.save()
        
        order.save()
        return Response({"status": "Payment verified successfully"}, status=status.HTTP_200_OK)
    except razorpay.errors.SignatureVerificationError:
        return Response({"error": "Payment validation failed"}, status=status.HTTP_400_BAD_REQUEST)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    try:
        data = request.data
        if User.objects.filter(email=data.get('email')).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(
            email=data.get('email'),
            name=data.get('name'),
            password=data.get('password'),
            role='user'
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    try:
        data = request.data
        email = data.get('email')
        password = data.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_user(request):
    logout(request)
    return Response({'status': 'Logged out successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
