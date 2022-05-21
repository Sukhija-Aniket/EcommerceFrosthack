from ctypes import addressof
from tkinter import CASCADE
from unicodedata import category
from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

app_name = 'core'

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport Wear'),
    ('OW', 'OutWear')
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return self.title


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class user(models.Model):
    name = models.CharField(max_length=200)
    # address = models.ForeignKey(Address, on_delete=models.CASCADE)
    phone_num = PhoneNumberField()
    email = models.EmailField()
    pwd = models.CharField(max_length=200)

class Address(models.Model):
    User = models.ForeignKey(user, on_delete=CASCADE)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    Hno = models.CharField(max_length=200)

# class payment(models.Model):
#     amount = models.IntegerField()



