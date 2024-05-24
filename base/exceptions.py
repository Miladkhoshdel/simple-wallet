from rest_framework.exceptions import APIException

class InsufficientFundsError(APIException):
    """
    Custom exception class for handling insufficient funds errors.

    This class extends the built-in APIException class and is used to handle 
    errors related to insufficient funds during API operations. It provides 
    a default HTTP status code, detail message, and error code for such errors.

    Attributes:
        status_code (int): The HTTP status code associated with the error (default: 402).
        default_detail (str): The default detail message for the error (default: 'Insufficient funds').
        default_code (str): The default error code for the error (default: 'insufficient_funds').
    """
    status_code = 402
    default_detail = 'Insufficient funds'
    default_code = 'insufficient_funds'

class BankException(Exception):
    """
    Custom exception class for handling bank-related errors.

    This class extends the built-in Exception class and is used to handle 
    specific errors related to bank operations. It allows for a custom error 
    message to be passed and stored.

    Attributes:
        message (str): The error message describing the exception.
    
    Methods:
        __init__(message): Initializes the BankException with the provided message.
    """
    def __init__(self, message):
        """
        Initializes the BankException with a custom error message.

        Args:
            message (str): The error message describing the exception.
        """
        self.message = message
        super().__init__(self.message)
