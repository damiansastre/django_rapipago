from django.test import TestCase
from django.utils import timezone
from .models import Customer, Invoice
from .serializers import ReadOnlyFullCustomerSerializer, ReadOnlyInvoiceSerializer, QuerySerializer, PaymentSerializer
import datetime

class CoreTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(external_id="12354",
                                                name="Pepe",
                                                last_name="Mustaine")

        self.invoice = Invoice.objects.create(customer=self.customer,
                                              creation_date=timezone.now(),
                                              expiration_date=timezone.now() + datetime.timedelta(hours=3),
                                              barcode='TESTBARCODE1234',
                                              amount=100.00)


    def test_customer_serializer(self):
        serializer = ReadOnlyFullCustomerSerializer(self.customer).data

    def test_invoice_serializer(self):
        serializer = ReadOnlyInvoiceSerializer(self.invoice).data
        self.assertEqual(serializer['importe'], '00000100.00')

    def test_query_serializer(self):
        data = {"id_clave": self.customer.external_id,
                "cod_trx": "1234",
                "canal": "rapipago",
                "fecha_hora_operacion": "1990-12-30 20:20:10"}
        serializer = QuerySerializer(data=data)
        serializer.is_valid()
        print(serializer.data)

    def test_payment_serializer(self):
        data = {"id_numero": self.customer.external_id,
                "cod_trx": "1234",
                "canal": "rapipago",
                "importe": self.invoice._amount,
                "barra": self.invoice.barcode,
                "fecha_hora_operacion": "1990-12-30 20:20:10"}
        serializer = PaymentSerializer(data=data)
        serializer.is_valid()
        print(serializer.data)