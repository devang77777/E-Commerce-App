from django import template
from django.contrib.auth import get_user_model
from shop.models import Product, Order, Contact

register = template.Library()


@register.simple_tag
def product_count():
    return Product.objects.count()


@register.simple_tag
def order_count():
    return Order.objects.count()


@register.simple_tag
def user_count():
    User = get_user_model()
    return User.objects.count()


@register.simple_tag
def contact_count():
    return Contact.objects.count()

