from rest_framework import serializers
from wallets.models import Wallet, Transaction


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class DepositSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=0)

    def validate_amount(self, value):
        """
        Check that the amount is a positive integer.
        """
        if value <= 0:
            raise serializers.ValidationError("Deposit amount must be greater than zero.")
        return value