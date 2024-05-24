from rest_framework.exceptions import APIException

class InsufficientFundsError(APIException):
    status_code = 402
    default_detail = 'Insufficient funds'
    default_code = 'insufficient_funds'

class BankException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
