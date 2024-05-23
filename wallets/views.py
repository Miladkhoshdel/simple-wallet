from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from wallets.models import Wallet, Transaction
from wallets.serializers import DepositSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status

from wallets.models import Wallet
from wallets.serializers import WalletSerializer


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
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class ScheduleWithdrawView(APIView):
    def post(self, request, *args, **kwargs):
        # todo: implement withdraw logic
        pass
        return Response({})

