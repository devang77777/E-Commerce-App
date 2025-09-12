

# from django.contrib import admin
# from django import forms
# from django.forms import MultipleFileInput
# from .models import Product, ProductImage, Contact, Order, OrderUpdate

# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 5  # Allow adding up to 5 images at once
#     fields = ('image',)
#     show_change_link = True

# class ProductAdminForm(forms.ModelForm):
#     images = forms.FileField(widget=MultipleFileInput(), required=False)

#     class Meta:
#         model = Product
#         fields = '__all__'

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         if commit:
#             instance.save()
#         images = self.cleaned_data.get('images')
#         if images:
#             for image in images:
#                 ProductImage.objects.create(product=instance, image=image)
#         return instance

# class ProductAdmin(admin.ModelAdmin):
#     form = ProductAdminForm
#     inlines = [ProductImageInline]
#     list_display = ('product_name', 'category', 'subcategory', 'price', 'pub_date', 'image_preview')
#     list_filter = ('category', 'subcategory', 'pub_date', 'price')
#     search_fields = ('product_name', 'category', 'subcategory', 'desc')
#     list_per_page = 25
#     ordering = ('-pub_date',)

#     def image_preview(self, obj):
#         if obj.image:
#             return f'<img src="{obj.image.url}" width="50" height="50" style="border-radius: 5px;" />'
#         return "No Image"
#     image_preview.allow_tags = True
#     image_preview.short_description = 'Preview'

# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('order_id', 'name', 'email', 'amount', 'city', 'state', 'razorpay_order_id', 'phone')
#     list_filter = ('state', 'city', 'amount')
#     search_fields = ('name', 'email', 'phone', 'order_id', 'razorpay_order_id')
#     readonly_fields = ('order_id', 'razorpay_order_id')
#     list_per_page = 25

# class OrderUpdateAdmin(admin.ModelAdmin):
#     list_display = ('update_id', 'order_id', 'razorpay_order_id', 'update_desc', 'timestamp')
#     list_filter = ('timestamp',)
#     search_fields = ('order_id', 'razorpay_order_id', 'update_desc')
#     readonly_fields = ('update_id', 'timestamp', 'razorpay_order_id')
#     list_per_page = 25

#     def save_model(self, request, obj, form, change):
#         # Auto-populate razorpay_order_id from the related Order; prevent manual edits
#         try:
#             order = Order.objects.get(order_id=obj.order_id)
#             obj.razorpay_order_id = order.razorpay_order_id
#         except Order.DoesNotExist:
#             pass
#         super().save_model(request, obj, form, change)

# class ContactAdmin(admin.ModelAdmin):
#     list_display = ('msg_id', 'name', 'email', 'phone')
#     search_fields = ('name', 'email', 'phone')
#     list_per_page = 25

# class ProductImageAdmin(admin.ModelAdmin):
#     list_display = ('product', 'image_preview', 'created_at')
#     list_filter = ('product__category', 'product__subcategory')
#     search_fields = ('product__product_name',)
#     list_per_page = 25
    
#     def image_preview(self, obj):
#         if obj.image:
#             return f'<img src="{obj.image.url}" width="50" height="50" style="border-radius: 5px;" />'
#         return "No Image"
#     image_preview.allow_tags = True
#     image_preview.short_description = 'Preview'
    
#     def created_at(self, obj):
#         return obj.product.pub_date
#     created_at.short_description = 'Product Date'

# admin.site.register(Product, ProductAdmin)
# admin.site.register(ProductImage, ProductImageAdmin)
# admin.site.register(Contact, ContactAdmin)
# admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderUpdate, OrderUpdateAdmin)

from django.contrib import admin
from django import forms
from django.forms import ClearableFileInput
from .models import Product, ProductImage, Contact, Order, OrderUpdate


# Custom MultipleFileInput
class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5
    fields = ('image',)
    show_change_link = True


class ProductAdminForm(forms.ModelForm):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True}),
        required=False
    )

    class Meta:
        model = Product
        fields = '__all__'

    def is_multipart(self):
        return True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()

        images = self.cleaned_data.get('images')   # ✅ cleaned_data is correct
        if images:
            # If multiple files uploaded, Django gives a list
            if isinstance(images, (list, tuple)):
                for image in images:
                    ProductImage.objects.create(product=instance, image=image)
            else:
                ProductImage.objects.create(product=instance, image=images)

        return instance


class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [ProductImageInline]
    list_display = ('product_name', 'category', 'subcategory', 'price', 'pub_date', 'image_preview')
    list_filter = ('category', 'subcategory', 'pub_date', 'price')
    search_fields = ('product_name', 'category', 'subcategory', 'desc')
    list_per_page = 25
    ordering = ('-pub_date',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="border-radius: 5px;" />'
        return "No Image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'name', 'email', 'amount', 'city', 'state', 'razorpay_order_id', 'phone')
    list_filter = ('state', 'city', 'amount')
    search_fields = ('name', 'email', 'phone', 'order_id', 'razorpay_order_id')
    readonly_fields = ('order_id', 'razorpay_order_id')
    list_per_page = 25


class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ('update_id', 'order_id', 'razorpay_order_id', 'update_desc', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('order_id', 'razorpay_order_id', 'update_desc')
    readonly_fields = ('update_id', 'timestamp', 'razorpay_order_id')
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        try:
            order = Order.objects.get(order_id=obj.order_id)
            obj.razorpay_order_id = order.razorpay_order_id
        except Order.DoesNotExist:
            pass
        super().save_model(request, obj, form, change)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('msg_id', 'name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')
    list_per_page = 25


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'created_at')
    list_filter = ('product__category', 'product__subcategory')
    search_fields = ('product__product_name',)
    list_per_page = 25

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="border-radius: 5px;" />'
        return "No Image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'

    def created_at(self, obj):
        return obj.product.pub_date
    created_at.short_description = 'Product Date'


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderUpdate, OrderUpdateAdmin)
