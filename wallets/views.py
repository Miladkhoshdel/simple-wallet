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
    serializer_class = WalletSerializer


class RetrieveWalletView(RetrieveAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()
    
    lookup_field = "uuid"


"""
{

"amount":10
}
"""
class CreateDepositView(APIView):
    def post(self, reqeust, uuid, *args, **kwargs):
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
    def post(self, reqeust, uuid, *args, **kwargs):
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

{
"amount":10,
"scheduled_time":"2024-05-24 09:00:00"
}
class ScheduleWithdrawView(APIView):
    def post(self, request, uuid, *args, **kwargs):
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
            # process_withdrawal.apply_async(args=(scheduled_withdrawal.id,), eta=scheduled_time)

            return Response({'status': 'success', 'message': 'Withdrawal scheduled'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

