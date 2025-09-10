

from django.contrib import admin
from django import forms
from .models import Product, ProductImage, Contact, Order, OrderUpdate

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAdminForm(forms.ModelForm):
    class MultipleFileInput(forms.ClearableFileInput):
        allow_multiple_selected = True

    images = forms.FileField(
        widget=MultipleFileInput(attrs={"multiple": True}),
        required=False,
        help_text="Select multiple images to upload",
    )

    class Meta:
        model = Product
        fields = "__all__"

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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        files = request.FILES.getlist("images")
        for uploaded_file in files:
            ProductImage.objects.create(product=obj, image=uploaded_file)

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
        # Auto-populate razorpay_order_id from the related Order; prevent manual edits
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