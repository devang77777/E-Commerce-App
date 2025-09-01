# from django.contrib import admin
# from .models import Product, ProductImage
# from .models import Product,Contact,Order,OrderUpdate

# # Register your models here.\
# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1

# class ProductAdmin(admin.ModelAdmin):
#     inlines = [ProductImageInline]

# admin.site.register(Product, ProductAdmin)
# admin.site.register(Product) 
# admin.site.register(Contact) 
# admin.site.register(Order) 
# admin.site.register(OrderUpdate) 

from django.contrib import admin
from .models import Product, ProductImage, Contact, Order, OrderUpdate

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(OrderUpdate)