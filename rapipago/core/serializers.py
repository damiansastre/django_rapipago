from rest_framework import serializers
from django.utils import timezone
from .models import Customer, Invoice, PAYED, REFUNDED, PENDING
from .exceptions import RapiPagoResponseCode, RapiPagoException
import datetime


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['id', 'external_id', 'name', 'last_name']


class InvoiceSerializer(serializers.ModelSerializer):
    ttl = serializers.IntegerField(write_only=True)
    customer_external_id = serializers.CharField(write_only=True)

    class Meta:
        model = Invoice
        fields = ['customer_external_id', 'customer', 'external_id', 'extra_data',
                  'expiration_date', 'ttl', 'barcode', 'amount', 'status']
        read_only_fields = ['expiration_date', 'customer', 'status']

    def validate_customer_external_id(self, value):
        try:
            customer = Customer.objects.get(external_id=value)
        except Customer.DoesNotExist:
            raise serializers.ValidationError('User Does Not Exist')
        return customer

    def validate(self, data):
        ttl = data.pop('ttl')
        data['expiration_date'] = timezone.now() + datetime.timedelta(seconds=ttl)
        data['customer'] = data.pop('customer_external_id')
        return data

class ReadOnlyInvoiceSerializer(serializers.ModelSerializer):
    id_numero = serializers.CharField(source='id')
    fecha_vencimiento = serializers.DateTimeField(source='expiration_date', format="%Y-%m-%d")
    fecha_emision = serializers.DateTimeField(source='creation_date', format="%Y-%m-%d")
    importe = serializers.SerializerMethodField('get_amount')
    barra = serializers.CharField(source='barcode')
    texto1 = serializers.SerializerMethodField('get_texto1')

    class Meta:
        model = Invoice
        fields = ['id_numero', 'fecha_vencimiento', 'fecha_emision', 'importe', 'barra', 'texto1']
        read_only_fields = ['id_numero', 'fecha_vencimiento', 'fecha_emision', 'importe', 'barra', 'texto1']

    def get_amount(self, obj):
        return obj._amount

    def get_texto1(self, obj):
        return obj.extra_data if obj.extra_data else ''


class ReadOnlyFullCustomerSerializer(serializers.ModelSerializer):
    id_clave = serializers.CharField(source='external_id')
    nombre = serializers.CharField(source='name')
    apellido = serializers.CharField(source='last_name')
    facturas = ReadOnlyInvoiceSerializer(source='invoices', many=True)

    class Meta:
        model = Customer
        fields = ['id_clave', 'nombre', 'apellido', 'facturas']
        read_only_fields = ['id_clave', 'nombre', 'apellido', 'facturas']


class QuerySerializer(serializers.Serializer):
    id_clave = serializers.CharField()
    cod_trx = serializers.CharField(max_length=22)
    canal = serializers.CharField(max_length=50)
    fecha_hora_operacion = serializers.DateTimeField(format='%Y%m%d %H:%M:%S')

    def validate_id_clave(self, value):
        try:
            return Customer.objects.get(external_id=value)
        except Customer.DoesNotExist:
            raise RapiPagoException(RapiPagoResponseCode.CLIENT_DOES_NOT_EXIST)

    def to_representation(self, value):
        reponse_code = RapiPagoResponseCode.OK
        payload = {}
        customer = value['id_clave']
        payload['id_clave'] = customer.external_id
        payload['nombre'] = customer.name
        payload['apellido'] = customer.last_name
        payload['cod_trx'] = value['cod_trx']
        payload['msg'] = reponse_code.description
        payload['codigo_respuesta'] = reponse_code.code
        payload['dato_adicional'] = 'Dato'
        payload['facturas'] = customer.invoices.filter(status=PENDING)

        return QueryResponseSerializer(payload).data

    def validate(self, data):
        customer = data['id_clave']
        if not customer.invoices.filter(status=PENDING).exists():
            raise RapiPagoException(RapiPagoResponseCode.NO_INVOICES_AVAILABLE)
        return data


class QueryResponseSerializer(serializers.Serializer):
    id_clave = serializers.CharField()
    nombre = serializers.CharField()
    apellido = serializers.CharField()
    cod_trx = serializers.CharField(max_length=22)
    codigo_respuesta = serializers.CharField()
    msg = serializers.CharField()
    dato_adicional = serializers.CharField(allow_blank=True)
    facturas = ReadOnlyInvoiceSerializer(many=True)


class PaymentSerializer(serializers.Serializer):
    id_numero = serializers.CharField()
    cod_trx = serializers.CharField(max_length=22)
    canal = serializers.CharField(max_length=50)
    importe = serializers.CharField(max_length=11)
    barra = serializers.CharField(max_length=22)
    fecha_hora_operacion = serializers.DateTimeField(format='%Y%m%d %H:%M:%S')

    def to_representation(self, invoice):
        return PaymentResponseSerializer(invoice).data

    def validate_id_numero(self, value):
        try:
            return Customer.objects.get(external_id=value)
        except Customer.DoesNotExist:
            raise RapiPagoException(RapiPagoResponseCode.CLIENT_DOES_NOT_EXIST)

    def validate_importe(self, value):
        return float(value)

    def validate(self, data):
        try:
            invoice = Invoice.objects.get(customer=data['id_numero'],
                                          barcode=data['barra'])
        except Invoice.DoesNotExist:
            raise RapiPagoException(RapiPagoResponseCode.NO_INVOICES_AVAILABLE)
        else:
            if invoice.status == PAYED:
                raise RapiPagoException(RapiPagoResponseCode.INVALID_OPERATION)
            if invoice.status == REFUNDED:
                raise RapiPagoException(RapiPagoResponseCode.ALREADY_REVERSED)
        invoice.status = PAYED
        invoice.payment_id = data['cod_trx']
        invoice.payment_date = timezone.now()
        invoice.save()
        return invoice

class PaymentResponseSerializer(serializers.ModelSerializer):
    id_numero = serializers.CharField(source='customer.external_id')
    cod_trx = serializers.CharField(max_length=22, source='payment_id')
    barra = serializers.CharField(max_length=22, source='barcode')
    fecha_hora_operacion = serializers.DateTimeField(format='%Y%m%d %H:%M:%S', source='payment_date')
    codigo_respuesta = serializers.CharField(default=RapiPagoResponseCode.OK.code)
    msg = serializers.CharField(default=RapiPagoResponseCode.OK.description)

    class Meta:
        model = Invoice
        fields = ['id_numero', 'cod_trx', 'barra', 'fecha_hora_operacion', 'codigo_respuesta', 'msg']