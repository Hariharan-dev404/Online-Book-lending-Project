import os, sys, django
sys.path.append('h:/Online_BookLending/Online-Book-lending-Project/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_lending_backend.settings')
django.setup()

from django.test import RequestFactory
from api.views import admin_verify_payment
from api.models import Order, User
import traceback
import json

o = Order.objects.first()
if not o:
    print("NO ORDER")
    sys.exit()

print("Order ID:", o.id, "Type:", o.order_type)
admin = User.objects.get(email='hariharan.moct@gmail.com')
rf = RequestFactory()
req = rf.post('/api/verify-payment/{}/'.format(o.id), json.dumps({'action':'verify'}), content_type='application/json')
req.user = admin

try:
    res = admin_verify_payment(req, o.id)
    print("RES STATUS:", res.status_code)
    try:
        print("RES CONTENT:", res.data)
    except:
        print("RES CONTENT:", res.content)
except Exception as e:
    traceback.print_exc()
