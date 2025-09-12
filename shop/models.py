from django.db import models

# Create your models here.

class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to='shop/images', default="")

    def __str__(self):
        return self.product_name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="shop/images/")

    def __str__(self):
        return f"{self.product.product_name} Image"
    
class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")


    def __str__(self):
        return self.name

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField( default=0)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=111)
    address = models.CharField(max_length=111)
    city = models.CharField(max_length=111)
    state = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=111)
    phone = models.CharField(max_length=111, default="")
    product_names = models.TextField(blank=True, null=True)
    product_descs = models.TextField(blank=True, null=True)
    total_quantity = models.IntegerField(default=0)
    razorpay_order_id = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.order_id} - {self.name} (₹{self.amount})"

class OrderUpdate(models.Model):
    update_id  = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    razorpay_order_id = models.CharField(max_length=64, blank=True, null=True)
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order_id}: {self.update_desc[:50]}{'...' if len(self.update_desc) > 50 else ''}"
