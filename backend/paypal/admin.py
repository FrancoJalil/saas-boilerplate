from django.contrib import admin
from .models import PaypalProductModel, PaypalProductModelAdmin, Purchase

# Register your models here.
admin.site.register(PaypalProductModel, PaypalProductModelAdmin)
admin.site.register(Purchase)

