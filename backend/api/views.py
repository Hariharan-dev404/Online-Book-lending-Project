from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from .models import Book, Order, User
from .serializers import BookSerializer, OrderSerializer, UserSerializer
from django.conf import settings



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
        from rest_framework.exceptions import ValidationError
        book = serializer.validated_data.get('book')
        order_type = serializer.validated_data.get('order_type')
        quantity = serializer.validated_data.get('quantity', 1)
        
        if quantity > book.stock:
            raise ValidationError("Not enough stock")
            
        lending_fee = 0
        deposit_amount = 0
        total_amount = 0
        
        if order_type == 'buy':
            total_amount = book.price * quantity
        elif order_type == 'lend':
            lending_fee = book.lending_price if book.lending_price and book.lending_price > 0 else book.price
            deposit_amount = book.price
            total_amount = lending_fee + deposit_amount
            quantity = 1
            
        serializer.save(user=self.request.user, lending_fee=lending_fee, deposit_amount=deposit_amount, total_amount=total_amount, quantity=quantity)

@api_view(['POST'])
def admin_verify_payment(request, pk):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return Response({"error": "Admin privileges required"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from datetime import timedelta
        from django.utils.timezone import now
        from django.core.mail import send_mail
        from django.conf import settings
        
        order = Order.objects.get(pk=pk)
        action = request.data.get('action') # 'verify' or 'reject'
        
        if action == 'verify':
            if order.payment_status != 'success':
                order.payment_status = 'success'
                
                # Date Logic
                if order.order_type == 'lend':
                    order.delivery_date = now().date() + timedelta(days=3)
                    order.return_date = order.delivery_date + timedelta(days=7)
                else:
                    order.delivery_date = now().date() + timedelta(days=4)
                    
                order.save()
                
                # Reduce stock
                book = order.book
                if book.stock > 0:
                    book.stock -= order.quantity
                    if book.stock <= 0:
                        book.status = 'sold'
                    book.save()
                    
                # Send Success Mail
                # Send Success Mail
                try:
                    to_email = order.user.email if order.user else 'test@example.com' # fallback
                    
                    if order.order_type == 'lend':
                        msg = f"""Dear {order.user_name},

Thank you for your order! Your payment has been successfully verified.
Your estimated delivery date is {order.delivery_date.strftime('%Y-%m-%d')}.
Please return the borrowed book by {order.return_date.strftime('%Y-%m-%d')}.

Return Instructions:
Please return the book safely. The return courier charges are your responsibility.
Your deposit will be refunded after we receive the book in good condition.

Return Address:
PageLoft Library
335, Groove Street, Chennai
Tamil Nadu, India

Thank you for using PageLoft."""
                        subject = 'Lending Confirmed - PageLoft'
                    else:
                        msg = f"Thank you for your order!\n\nYour payment has been successfully verified. Your estimated delivery date is {order.delivery_date.strftime('%Y-%m-%d')}."
                        subject = 'Order Confirmed - PageLoft'
                        
                    send_mail(
                        subject,
                        msg,
                        settings.DEFAULT_FROM_EMAIL,
                        [to_email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Email error: {e}")

            return Response({"message": "Order payment verified successfully."}, status=status.HTTP_200_OK)

        elif action == 'reject':
            if order.payment_status != 'rejected':
                order.payment_status = 'rejected'
                order.save()
                
                # Send Reject Mail
                try:
                    to_email = order.user.email if order.user else 'test@example.com'
                    send_mail(
                        'Payment Verification Failed',
                        'We were unable to verify your payment. Please check the details and try again or contact support.',
                        settings.DEFAULT_FROM_EMAIL,
                        [to_email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Email error: {e}")
                    
            return Response({"message": "Order payment rejected."}, status=status.HTTP_200_OK)
            
        else:
            return Response({"error": "Invalid action specified. Must be 'verify' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

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

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def forgot_password(request):
    try:
        from django.utils.timezone import now
        from datetime import timedelta
        import random
        from django.core.mail import send_mail
        from django.conf import settings
        
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        user.reset_otp = otp
        user.reset_otp_expiry = now() + timedelta(minutes=10)
        user.save()
        
        # Send OTP via Email
        send_mail(
            'Password Reset OTP - PageLoft',
            f'Your OTP for resetting your password is: {otp}\n\nThis OTP is valid for 10 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return Response({'message': 'OTP sent successfully to your email.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    try:
        from django.utils.timezone import now
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not all([email, otp, new_password]):
            return Response({'error': 'Email, OTP, and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
        if user.reset_otp != otp:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
        if user.reset_otp_expiry and user.reset_otp_expiry < now():
            return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Valid OTP, Reset password
        user.set_password(new_password)
        user.reset_otp = None
        user.reset_otp_expiry = None
        user.save()
        
        return Response({'message': 'Password reset successfully. You can now login with your new password.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_refund_deposit(request, pk):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return Response({"error": "Admin privileges required"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        order = Order.objects.get(pk=pk)
        if order.order_type != 'lend':
            return Response({"error": "Only lending orders have a deposit."}, status=status.HTTP_400_BAD_REQUEST)
        
        if order.refund_status == 'completed':
            return Response({"error": "Deposit is already refunded."}, status=status.HTTP_400_BAD_REQUEST)
            
        order.refund_status = 'completed'
        order.save()
        
        # Send Email
        try:
            to_email = order.user.email if order.user else 'test@example.com'
            send_mail(
                'Deposit Refunded',
                'Your deposit has been successfully refunded after book return. Thank you for using PageLoft.',
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Email error: {e}")
            
        return Response({"message": "Deposit refunded successfully."}, status=status.HTTP_200_OK)
        
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def admin_update_tracking(request, pk):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return Response({"error": "Admin privileges required"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        order = Order.objects.get(pk=pk)
        tracking_id = request.data.get('tracking_id')
        delivery_status = request.data.get('delivery_status')
        
        status_changed_to_shipped = False
        if delivery_status and delivery_status != order.delivery_status:
            if delivery_status == 'shipped' and order.delivery_status != 'shipped':
                status_changed_to_shipped = True
            order.delivery_status = delivery_status
            
        if tracking_id is not None:
            order.tracking_id = tracking_id
            
        order.save()
        
        if status_changed_to_shipped:
            from django.utils.timezone import now
            from datetime import timedelta
            order.delivery_date = now().date() + timedelta(days=4)
            order.save()
            try:
                to_email = order.user.email if order.user else 'test@example.com'
                msg = f"Your order has been shipped.\n\nEstimated delivery in 4 days from shipping date ({order.delivery_date.strftime('%Y-%m-%d')})."
                if order.tracking_id:
                    msg += f"\nTracking ID: {order.tracking_id}"
                msg += "\n\nIf you face any issues, please contact support."
                
                send_mail(
                    'Your Order is On the Way',
                    msg,
                    settings.DEFAULT_FROM_EMAIL,
                    [to_email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email error: {e}")
                
        return Response({"message": "Tracking updated successfully."}, status=status.HTTP_200_OK)
        
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
