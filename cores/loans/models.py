from django.db import models
from django.contrib.auth.models import User
from inventory.models import Host
from django.utils import timezone

class Customer(models.Model):
    name = models.CharField(max_length=120)
    contact_name = models.CharField(blank=True, null=True, max_length=120)
    contact_role = models.CharField(blank=True, null=True, max_length=120)
    contact_email = models.EmailField(blank=True, null=True)
    internal_contact = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

class Loan(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='loans')
    start = models.DateTimeField(help_text='When was this loan supposed to start?')
    due_return = models.DateTimeField(help_text='When are we expecting this to be back?')
    returned_date = models.DateTimeField(help_text='When did this actually get back to us?', blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT, help_text='Individual responsible for the loan')
    returned = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.host.hostname} to {self.customer.name}'