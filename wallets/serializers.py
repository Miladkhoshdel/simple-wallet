from rest_framework import serializers
from wallets.models import Wallet, Transaction
from django.utils import timezone
from decimal import Decimal

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.00'))

    def validate_amount(self, value):
        """
        Check that the amount is a positive integer.
        """
        if value <= 0:
            raise serializers.ValidationError("Deposit amount must be greater than zero.")
        return value
    
class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.00'))

    def validate_amount(self, value):
        """
        Check that the amount is a positive integer.
        """
        if value <= 0:
            raise serializers.ValidationError("Withdraw amount must be greater than zero.")
        return value
    
class ScheduleWithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.00'))
    scheduled_time = serializers.DateTimeField()

    def validate_amount(self, value):
        """
        Check that the amount is a positive integer.
        """
        if value <= 0:
            raise serializers.ValidationError("Deposit amount must be greater than zero.")
        return value
    
    def validate_scheduled_time(self, value):
        """
        Check that the datetime is a valid datetime.
        """
        if value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future")
        return value