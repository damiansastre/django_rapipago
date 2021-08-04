from django.db import models

PENDING = 0
PAYED = 1
REFUNDED = -1

class Customer(models.Model):
    external_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    additional_data = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return '[{}]: {} {}'.format(self.external_id, self.name, self.last_name)


class Invoice(models.Model):
    INVOICE_CHOICES = ((PENDING, 'pending'),
                       (PAYED, 'payed'),
                       (REFUNDED, 'refunded'))
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='invoices')
    external_id = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    payment_date = models.DateTimeField(null=True, blank=True)
    barcode = models.CharField(max_length=22, unique=True)
    amount = models.FloatField()
    extra_data = models.CharField(max_length=30, null=True, blank=True)
    status = models.IntegerField(choices=INVOICE_CHOICES, default=0)

    @property
    def _amount(self):
        return '{:011.2f}'.format(self.amount)

    def __str__(self):
        return '[{}] {} {}: {} : {}'.format(self.barcode,
                                                     self.customer.name,
                                                     self.customer.last_name,
                                                     self.amount,
                                                     self.status)


