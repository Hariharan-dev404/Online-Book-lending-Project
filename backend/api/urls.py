from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (BookViewSet, OrderViewSet, admin_verify_payment, register_user, 
                    login_user, logout_user, current_user, admin_refund_deposit, admin_update_tracking,
                    forgot_password, reset_password)

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('verify-payment/<int:pk>/', admin_verify_payment, name='admin_verify_payment'),
    path('admin/orders/<int:pk>/refund/', admin_refund_deposit, name='admin_refund_deposit'),
    path('admin/orders/<int:pk>/tracking/', admin_update_tracking, name='admin_update_tracking'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('user/', current_user, name='current_user'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
]
