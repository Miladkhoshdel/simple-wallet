from rest_framework import serializers
from wallets.models import Wallet, Transaction
from django.utils import timezone
from decimal import Decimal

class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for the Wallet model.

    This serializer class is used to serialize and deserialize Wallet model instances
    for use in Django REST Framework views. It specifies the model and fields to include
    or exclude during serialization and deserialization.

    Attributes:
        Meta (class): Inner class containing metadata for the serializer.
            - model (Model): The Django model class to serialize/deserialize (Wallet).
            - fields (tuple): A tuple of field names to include in the serialized output.
                Here, '__all__' is used to include all fields from the Wallet model.
    """
    class Meta:
        model = Wallet
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transaction model.

    This serializer class is used to serialize and deserialize Transaction model instances
    for use in Django REST Framework views. It specifies the model and fields to include
    or exclude during serialization and deserialization.

    Attributes:
        Meta (class): Inner class containing metadata for the serializer.
            - model (Model): The Django model class to serialize/deserialize (Transaction).
            - fields (tuple): A tuple of field names to include in the serialized output.
                Here, '__all__' is used to include all fields from the Transaction model.
    """
    class Meta:
        model = Transaction
        fields = '__all__'

class DepositSerializer(serializers.Serializer):
    """
    Serializer for validating deposit amount.

    This serializer class is used to validate the amount field for deposit transactions.
    It ensures that the amount provided is a positive decimal value.

    Attributes:
        amount (DecimalField): A decimal field representing the amount to be deposited.

    Methods:
        validate_amount(value): Custom validation method to check if the amount is positive.
            It raises a validation error if the amount is not greater than zero.
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.00'))

    def validate_amount(self, value):
        """
        Check that the amount is a positive decimal value.

        Args:
            value (decimal.Decimal): The value of the amount to be validated.

        Returns:
            decimal.Decimal: The validated amount if it is positive.

        Raises:
            serializers.ValidationError: If the amount is not greater than zero.
        """
        if value <= 0:
            raise serializers.ValidationError("Deposit amount must be greater than zero.")
        return value
    
class WithdrawSerializer(serializers.Serializer):
    """
    Serializer for validating withdrawal amount.

    This serializer class is used to validate the amount field for withdrawal transactions.
    It ensures that the amount provided is a positive decimal value.

    Attributes:
        amount (DecimalField): A decimal field representing the amount to be withdrawn.

    Methods:
        validate_amount(value): Custom validation method to check if the amount is positive.
            It raises a validation error if the amount is not greater than zero.
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.00'))

    def validate_amount(self, value):
        """
        Check that the amount is a positive decimal value.

        Args:
            value (decimal.Decimal): The value of the amount to be validated.

        Returns:
            decimal.Decimal: The validated amount if it is positive.

        Raises:
            serializers.ValidationError: If the amount is not greater than zero.
        """
        if value <= 0:
            raise serializers.ValidationError("Withdraw amount must be greater than zero.")
        return value
    
class ScheduleWithdrawSerializer(serializers.Serializer):
    """
    Serializer for validating scheduled withdrawal parameters.

    This serializer class is used to validate the amount and scheduled_time fields
    for scheduling withdrawal transactions. It ensures that the amount provided is
    a positive decimal value and that the scheduled time is a future datetime.

    Attributes:
        amount (DecimalField): A decimal field representing the amount to be withdrawn.
        scheduled_time (DateTimeField): A datetime field representing the scheduled time for withdrawal.

    Methods:
        validate_amount(value): Custom validation method to check if the amount is positive.
            It raises a validation error if the amount is not greater than zero.
        validate_scheduled_time(value): Custom validation method to check if the scheduled time
            is in the future. It raises a validation error if the scheduled time is not in the future.
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.00'))
    scheduled_time = serializers.DateTimeField()

    def validate_amount(self, value):
        """
        Check that the amount is a positive decimal value.

        Args:
            value (decimal.Decimal): The value of the amount to be validated.

        Returns:
            decimal.Decimal: The validated amount if it is positive.

        Raises:
            serializers.ValidationError: If the amount is not greater than zero.
        """
        if value <= 0:
            raise serializers.ValidationError("Deposit amount must be greater than zero.")
        return value
    
    def validate_scheduled_time(self, value):
        """
        Check that the datetime is a valid datetime and in the future.

        Args:
            value (datetime.datetime): The datetime value to be validated.

        Returns:
            datetime.datetime: The validated datetime if it is in the future.

        Raises:
            serializers.ValidationError: If the scheduled time is not in the future.
        """
        if value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future")
        return value