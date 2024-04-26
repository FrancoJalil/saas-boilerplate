from django.db import models
from user.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from paypal.helpers.products import create_product
from .permissions import IsSuperuserOrReadOnly
from django.contrib import admin

# Create your models here.

class PaypalProductModel(models.Model):

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    home_url = models.CharField(max_length=200)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'is_superuser': True})
    paypal_id_product = models.CharField(max_length=200, unique=True, help_text="The product ID will be generated once saved.")

    def __str__(self):
        return self.name

@receiver(post_save, sender=PaypalProductModel)
def my_function(sender, instance, created, **kwargs):
    if created:

        if not IsSuperuserOrReadOnly().has_permission(instance, None):
            return

        if instance.paypal_id_product == "":
            # If the product was not created in "tests.py" create it in paypal
            create_product(instance.name, instance.description, instance.home_url)

class PaypalProductModelAdmin(admin.ModelAdmin):
    readonly_fields = ('paypal_id_product',)
    
    
class Purchase(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(PaypalProductModel, on_delete=models.CASCADE)
    purchased_date = models.DateTimeField(auto_now_add=True)
    price = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.product} Purchased by {self.user}"


