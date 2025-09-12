# TODO: Fix item quantity issues and remove product_descs from Order model

## Tasks
- [x] Edit shop/models.py to remove product_descs field
- [x] Edit shop/views.py checkout view: remove product_descs extraction/setting, add item_quantities setting
- [x] Edit shop/views.py initiate_payment view: remove product_descs extraction/setting, add item_quantities setting
- [x] Run python manage.py makemigrations
- [x] Run python manage.py migrate
- [x] Test the changes to ensure item quantities work correctly
