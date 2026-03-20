from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, OrderViewSet, create_razorpay_order, verify_payment, register_user, login_user, logout_user, current_user

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-razorpay-order/', create_razorpay_order, name='create_razorpay_order'),
    path('verify-payment/', verify_payment, name='verify_payment'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('user/', current_user, name='current_user'),
]
