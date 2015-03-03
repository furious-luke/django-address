from django.db import models
from address.models import AddressField

class Example(models.Model):
    address = AddressField()
