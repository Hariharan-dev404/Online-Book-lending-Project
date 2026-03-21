import os, sys, django
sys.path.append('h:/Online_BookLending/Online-Book-lending-Project/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_lending_backend.settings')
django.setup()
from django.core.mail import send_mail
from django.conf import settings
import traceback

try:
    send_mail(
        'PageLoft Test Email',
        'If you are reading this, your Django SMTP setup is now perfectly synchronized with Google!',
        settings.DEFAULT_FROM_EMAIL,
        ['hariharan.moct@gmail.com'],
        fail_silently=False,
    )
    print('EMAIL SENT SUCCESSFULLY')
except Exception as e:
    traceback.print_exc()
