from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from .models import Customer, Invoice
from .serializers import QuerySerializer, CustomerSerializer, InvoiceSerializer,\
    PaymentSerializer, ReadOnlyFullCustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

    @action(detail=True, methods=['get'])
    def full(self, request, pk=None):
        customer = self.get_object()
        serializer = ReadOnlyFullCustomerSerializer(customer)
        return Response(serializer.data)


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()


class QueryAPIView(LoggingMixin, APIView):

    def post(self, request):
        serializer = QuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class PaymentAPIView(LoggingMixin, APIView):

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
