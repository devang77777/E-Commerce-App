



from django.shortcuts import render
from django.http import HttpResponse

from .models import Product, ProductImage, Contact, Order, OrderUpdate
from django.db.models import Q
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
def my_orders(request):
    user_email = request.user.email.strip()
    # Fetch orders for the user
    orders = Order.objects.filter(email__iexact=user_email).order_by('-order_id')
    print(f"Fetching orders for user email: '{user_email}', found: {orders.count()}")

    # Prepare combined list of orders with latest update info
    orders_with_updates = []
    for order in orders:
        latest_update = OrderUpdate.objects.filter(order_id=order.order_id).order_by('-timestamp').first()
        order_date = latest_update.timestamp if latest_update else None
        status = latest_update.update_desc if latest_update else "N/A"

        # Calculate total quantity from items_json
        total_qty = 0
        try:
            items = json.loads(order.items_json)
            total_qty = sum(item['qty'] for item in items.values())
        except (json.JSONDecodeError, KeyError, TypeError):
            total_qty = 0

        orders_with_updates.append({
            'order': order,
            'order_date': order_date,
            'status': status,
            'quantity': total_qty,
        })

    return render(request, 'shop/my_orders.html', {'orders': orders_with_updates, 'user_email': user_email})



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
    if request.method == "POST":
        orderId = request.POST.get('orderId', '').strip()
        try:
            # Normalize input
            orderId_norm = orderId.strip().strip('"').strip("'")
            # Allow lookup by our internal order_id OR Razorpay order id (exact/iexact)
            base_query = (
                (Q(order_id=int(orderId_norm)) if orderId_norm.isdigit() else Q()) |
                Q(razorpay_order_id__iexact=orderId_norm) |
                Q(razorpay_order_id=orderId_norm)
            )

            order_qs = Order.objects.filter(base_query).order_by('-order_id')

            # Fallback: search in OrderUpdate if Order didn't capture razorpay id historically
            if not order_qs.exists():
                upd = OrderUpdate.objects.filter(
                    Q(razorpay_order_id__iexact=orderId_norm) | Q(razorpay_order_id__icontains=orderId_norm)
                ).order_by('-timestamp').first()
                if upd:
                    order_qs = Order.objects.filter(order_id=upd.order_id)

            # Fuzzy fallback: partial/ci match on razorpay id
            if not order_qs.exists() and orderId_norm:
                order_qs = Order.objects.filter(razorpay_order_id__icontains=orderId_norm).order_by('-order_id')

            if order_qs.exists():
                order = order_qs.first()
                update_qs = OrderUpdate.objects.filter(order_id=order.order_id).order_by('timestamp')
                # Backfill missing razorpay ids on legacy updates
                if order.razorpay_order_id:
                    OrderUpdate.objects.filter(order_id=order.order_id, razorpay_order_id__isnull=True).update(razorpay_order_id=order.razorpay_order_id)
                updates = [{'text': u.update_desc, 'time': u.timestamp, 'razorpayOrderId': u.razorpay_order_id or ''} for u in update_qs]
                response = json.dumps({
                    "status": "success",
                    "updates": updates,
                    "itemsJson": order.items_json,
                    "orderId": order.order_id,
                    "razorpayOrderId": order.razorpay_order_id or ""
                }, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"no-item"}')
        except Exception as e:
            # Return error detail to help diagnose issues in development
            return HttpResponse(json.dumps({"status": "error", "message": str(e)}))

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
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        # Extract product names and descriptions from items_json
        product_names = []
        product_descs = []
        try:
            items = json.loads(items_json)
            for item in items:
                product_names.append(item.get('product_name', ''))
                product_descs.append(item.get('desc', ''))
        except Exception as e:
            print(f"Error parsing items_json: {e}")

        order = Order(
            items_json=items_json, name=name, email=email,
            address=address, city=city, state=state,
            zip_code=zip_code, phone=phone, amount=amount/100,
            product_names=', '.join(product_names),
            product_descs=', '.join(product_descs)
        )
        order.save()

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })
        # Save the Razorpay order id to our Order
        order.razorpay_order_id = razorpay_order.get("id")
        order.save(update_fields=["razorpay_order_id"])

        # Create update AFTER we have razorpay_order_id and copy it onto the update
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed", razorpay_order_id=order.razorpay_order_id)
        update.save()

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
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        # Extract product names and descriptions from items_json and calculate amount
        product_names = []
        product_descs = []
        total_amount = 0
        try:
            items = json.loads(items_json)
            for item_key, item_data in items.items():
                qty = item_data[0]
                price = item_data[2]
                total_amount += qty * price
                product_names.append(item_data[1])  # product_name
                product_descs.append('')  # desc not available in cart format, can be updated later
        except Exception as e:
            print(f"Error parsing items_json: {e}")
            # If items_json is invalid, cannot proceed
            return HttpResponse("Invalid cart data", status=400)

        # Always use calculated amount from cart items
        if total_amount <= 0:
            return HttpResponse("Cart is empty or invalid amount", status=400)

        amount = int(total_amount * 100)  # Razorpay uses paise

        # Save order in database
        order = Order(
            items_json=items_json, name=name, email=email,
            address=address, city=city, state=state,
            zip_code=zip_code, phone=phone, amount=amount/100,
            product_names=', '.join(product_names),
            product_descs=', '.join(product_descs)
        )
        order.save()

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

        # Create order update now that we have the razorpay id
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed", razorpay_order_id=order.razorpay_order_id)
        update.save()

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


