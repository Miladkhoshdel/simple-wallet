from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from wallets.models import Wallet, Transaction, ScheduledWithdrawal
from wallets.serializers import DepositSerializer, WithdrawSerializer, ScheduleWithdrawSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.utils import timezone
from django.db import models, transaction
from wallets.tasks import process_withdrawal
from django_celery_beat.models import ClockedSchedule, PeriodicTask
import json
from wallets.models import Wallet
from wallets.serializers import WalletSerializer
import datetime

class CreateWalletView(CreateAPIView):
    """
    API view for creating a new wallet.

    This view class extends the built-in CreateAPIView provided by Django REST Framework
    and is used to handle HTTP POST requests for creating new wallet instances. It specifies
    the serializer class to use for validating and processing the incoming data.

    Attributes:
        serializer_class (Serializer): The serializer class responsible for validating
            and processing the data for creating a new wallet instance.
    """
    serializer_class = WalletSerializer


class RetrieveWalletView(RetrieveAPIView):
    """
    API view for retrieving a wallet by its UUID.

    This view class extends the built-in RetrieveAPIView provided by Django REST Framework
    and is used to handle HTTP GET requests for retrieving a wallet instance by its UUID.
    It specifies the serializer class to use for serializing the retrieved wallet instance
    and sets the queryset to include all wallet instances.

    Attributes:
        serializer_class (Serializer): The serializer class responsible for serializing
            the retrieved wallet instance.
        queryset (QuerySet): The queryset containing all wallet instances.
        lookup_field (str): The name of the field used to retrieve a specific wallet instance.
            In this case, it's set to "uuid" to retrieve a wallet by its UUID.
    """
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()
    
    lookup_field = "uuid"


class CreateDepositView(APIView):
    """
    API view for creating a deposit transaction for a specific wallet.

    This view class extends the built-in APIView provided by Django REST Framework
    and is used to handle HTTP POST requests for creating deposit transactions
    for a specific wallet identified by its UUID. The request body should contain
    a JSON object with the amount to deposit.

    Attributes:
        serializer_class (Serializer): The serializer class responsible for validating
            the incoming data.
    
    Methods:
        post(request, uuid, *args, **kwargs): Handles HTTP POST requests for creating
            deposit transactions. It validates the incoming data, retrieves the wallet
            by its UUID, deposits the specified amount into the wallet, and returns
            the updated wallet details.
    """
    def post(self, reqeust, uuid, *args, **kwargs):
        """
        Handles HTTP POST requests for creating deposit transactions.

        Args:
            request (HttpRequest): The HTTP request object containing the request data.
            uuid (str): The UUID of the wallet for which the deposit transaction is to be created.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: A response containing the updated wallet details or an error message
                if the deposit operation fails.

        Raises:
            Http404: If the wallet with the specified UUID does not exist.

        Sample Request:
            {
            "amount":10
            }
        """
        serializer = DepositSerializer(data=self.request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            wallet = get_object_or_404(Wallet, uuid=uuid)
            try:
                wallet.deposit(amount)
                return Response({'uuid': wallet.uuid, 'new_balance': wallet.balance}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class CreateWithdrawView(APIView):
    """
    API view for creating a withdrawal transaction for a specific wallet.

    This view class extends the built-in APIView provided by Django REST Framework
    and is used to handle HTTP POST requests for creating withdrawal transactions
    for a specific wallet identified by its UUID. The request body should contain
    a JSON object with the amount to withdraw.

    Attributes:
        serializer_class (Serializer): The serializer class responsible for validating
            the incoming data.
    
    Methods:
        post(request, uuid, *args, **kwargs): Handles HTTP POST requests for creating
            withdrawal transactions. It validates the incoming data, retrieves the wallet
            by its UUID, withdraws the specified amount from the wallet, and returns
            the updated wallet details.
    """
    def post(self, reqeust, uuid, *args, **kwargs):
        """
        Handles HTTP POST requests for creating withdrawal transactions.

        Args:
            request (HttpRequest): The HTTP request object containing the request data.
            uuid (str): The UUID of the wallet from which the withdrawal transaction is to be created.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: A response containing the updated wallet details or an error message
                if the withdrawal operation fails.

        Raises:
            Http404: If the wallet with the specified UUID does not exist.

        Sample Request:
            {
            "amount":10
            }
        """
        serializer = WithdrawSerializer(data=self.request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            wallet = get_object_or_404(Wallet, uuid=uuid)
            try:
                wallet.withdraw(amount)
                return Response({'uuid': wallet.uuid, 'new_balance': wallet.balance}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleWithdrawView(APIView):
    """
    API view for scheduling a withdrawal from a specific wallet.

    This view class extends the built-in APIView provided by Django REST Framework
    and is used to handle HTTP POST requests for scheduling withdrawals from
    a specific wallet identified by its UUID. The request body should contain
    a JSON object with the amount to withdraw and the scheduled time for withdrawal.

    Attributes:
        serializer_class (Serializer): The serializer class responsible for validating
            the incoming data.
    
    Methods:
        post(request, uuid, *args, **kwargs): Handles HTTP POST requests for scheduling
            withdrawals. It validates the incoming data, retrieves the wallet
            by its UUID, schedules the withdrawal, creates a periodic task for
            processing the withdrawal, and returns a success response if the
            scheduling is successful.
    """
    def post(self, request, uuid, *args, **kwargs):
        """
        Handles HTTP POST requests for scheduling withdrawals.

        Args:
            request (HttpRequest): The HTTP request object containing the request data.
            uuid (str): The UUID of the wallet for which the withdrawal is to be scheduled.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: A response indicating the status of the withdrawal scheduling
                operation.

        Raises:
            Http404: If the wallet with the specified UUID does not exist.

        Sample Request:
            {
            "amount":10,
            "scheduled_time":"2024-05-24 09:00:00"
            }
        """
        serializer = ScheduleWithdrawSerializer(data=self.request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            scheduled_time = serializer.validated_data['scheduled_time']
            # scheduled_time = timezone.datetime.strptime(scheduled_time_str, '%Y-%m-%d %H:%M:%S')
            wallet = get_object_or_404(Wallet, uuid=uuid)
            with transaction.atomic():
                scheduled_withdrawal = ScheduledWithdrawal.objects.create(wallet=wallet, amount=amount, scheduled_time=scheduled_time)
                scheduled_withdrawal.save()

                wallet.schadule_withdraw(amount)
                clocked, created = ClockedSchedule.objects.get_or_create(
                    clocked_time=scheduled_time
                    )
            
                task = PeriodicTask.objects.create(
                    
                    clocked=clocked,
                    name=f"{uuid}-{amount}-withdraw-{datetime.datetime.now().timestamp()}",
                    task="wallets.tasks.process_withdrawal",
                    one_off=True,
                    queue="withdraw",
                    kwargs=json.dumps(
                        {
                            "scheduled_withdrawal_id": scheduled_withdrawal.id,
                        }
                    ),
                )

            return Response({'status': 'success', 'message': 'Withdrawal scheduled'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

