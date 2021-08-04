from rest_framework.views import exception_handler
from rest_framework import serializers
from rest_framework.response import Response
from django.conf import settings
from collections import namedtuple

RapiPagoResponseItem = namedtuple('RapiPagoExceptionItem', ['code', 'description'])

class RapiPagoResponseCode:

    OK = RapiPagoResponseItem("0", "Trx ok")
    DB_ERROR = RapiPagoResponseItem("1", "Error en BD")
    DUPLICATED_KEY = RapiPagoResponseItem("2", "Clave Duplicada")
    ALREADY_REVERSED = RapiPagoResponseItem("3", "Transaction ya reversada")
    PAYMENT_DOES_NOT_EXIST = RapiPagoResponseItem("4", "No existe el Pago")
    INVALID_OPERATION = RapiPagoResponseItem("5", "Operacion invalida")
    NO_INVOICES_AVAILABLE = RapiPagoResponseItem("6", "No existe el registro")
    CLIENT_DOES_NOT_EXIST = RapiPagoResponseItem("7", "Cliente no existe")
    CODE_VALIDATION_ERROR = RapiPagoResponseItem("8", "Error de validacion del codigo de cliente")
    INCORRECT_PARAMETERS = RapiPagoResponseItem("9", "parametros incorrectos o faltantes")
    INTERNAL_ERROR = RapiPagoResponseItem("10", "Error interno de la entidad")
    USER_HAS_NO_PERMISSION = RapiPagoResponseItem("11", "Usuario no habilitado para operar")
    OUT_OF_BUSINESS_HOURS = RapiPagoResponseItem("13", "Transaccion fuera de Horario")

class RapiPagoException(Exception):
    """Custom Exceptions for RapiPago Requests"""

    def __init__(self, code):
        self.message = code
        super().__init__(self.message)

def is_rapipago(url):
    return 'STO' in url

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    if is_rapipago(context['request'].path):
        rapipago_context = context['view'].request.data

        try:
            rapipago_context.pop('canal')
            rapipago_context.pop('importe')
        except:
            pass

        if isinstance(exc, RapiPagoException):
            rapipago_context['codigo_respuesta'] = exc.message.code
            rapipago_context['msg'] = exc.message.description
        else:
            if exc.status_code == 400:
                error = RapiPagoResponseCode.INCORRECT_PARAMETERS
            else:
                error = RapiPagoResponseCode.INTERNAL_ERROR

            rapipago_context['codigo_respuesta'] = error.code
            rapipago_context['msg'] = error.description

            if settings.DEBUG:
                rapipago_context['debug'] = exc.get_full_details()
        return Response(rapipago_context)

            # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response
