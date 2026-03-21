from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from api.models import Order

class Command(BaseCommand):
    help = 'Send reminder emails to users 1-2 days before return date'

    def handle(self, *args, **kwargs):
        # We find lending orders where return_date is within next 2 days
        today = timezone.now().date()
        target_date_start = today + timedelta(days=1)
        target_date_end = today + timedelta(days=2)
        
        # We only want to remind active un-refunded lending orders
        orders_to_remind = Order.objects.filter(
            order_type='lend',
            return_date__range=(target_date_start, target_date_end),
            refund_status='pending'
        )
        
        count = 0
        for order in orders_to_remind:
            try:
                to_email = order.user.email if order.user else None
                if to_email:
                    send_mail(
                        'Return Reminder - PageLoft',
                        f'Reminder: Please return the borrowed book "{order.book.title}" before the due date ({order.return_date.strftime("%Y-%m-%d")}) to avoid penalty.',
                        settings.DEFAULT_FROM_EMAIL,
                        [to_email],
                        fail_silently=True,
                    )
                    count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error sending email for order {order.id}: {e}"))
                
        self.stdout.write(self.style.SUCCESS(f"Successfully sent {count} reminder emails."))
