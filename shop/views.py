



from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, ProductImage, Contact, Order, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from PayTm import Checksum




MERCHANT_KEY = 'Your-Merchant-Key-Here'

def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

def searchMatch(query,item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query,item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod)!=0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success","updates":updates,"itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"no-item"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')

# def productView(request, myid):
#     product = Product.objects.filter(id=myid)
#     return render(request, 'shop/prodView.html', {'product':product[0]})
def productView(request, myid):
    product = Product.objects.get(id=myid)
    images = product.images.all()  # fetch all related ProductImage objects
    return render(request, 'shop/prodView.html', {'product': product, 'images': images})


import razorpay
from django.conf import settings

@login_required
def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = int(float(request.POST.get('amount', '0')) * 100)  # Razorpay uses paise
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        order = Order(
            items_json=items_json, name=name, email=email,
            address=address, city=city, state=state,
            zip_code=zip_code, phone=phone, amount=amount/100
        )
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })
        # Save the Razorpay order id to our Order
        order.razorpay_order_id = razorpay_order.get("id")
        order.save(update_fields=["razorpay_order_id"])

        context = {
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order_id": razorpay_order["id"],
            "amount": amount,
            "name": name,
            "email": email,
            "phone": phone,
        }
        return render(request, 'shop/payment.html', context)

    return render(request, 'shop/checkout.html')

@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})

def paymentstatus(request):
    success = request.GET.get("success", False)
    return render(request, "shop/paymentstatus.html", {"success": success})


@login_required
def initiate_payment(request):
    if request.method == "POST":
        # Get form data from checkout
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = int(float(request.POST.get('amount', '0')) * 100)  # Razorpay uses paise
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        # Save order in database
        order = Order(
            items_json=items_json, name=name, email=email,
            address=address, city=city, state=state,
            zip_code=zip_code, phone=phone, amount=amount/100
        )
        order.save()
        
        # Create order update
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()

        # Create Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })
        # Save the Razorpay order id to our Order
        order.razorpay_order_id = razorpay_order.get("id")
        order.save(update_fields=["razorpay_order_id"])

        # Pass details to payment template
        context = {
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order_id": razorpay_order["id"],
            "amount": amount,  # Keep as paise for Razorpay
            "display_amount": amount // 100,  # Convert to rupees for display
            "currency": "INR",
            "name": name,
            "email": email,
            "phone": phone,
        }
        return render(request, 'shop/payment.html', context)
    
    # If not POST, redirect to checkout
    return render(request, 'shop/checkout.html')


