import uuid

from django.db import models
from wallets.managers import WalletManager, TransactionManager
from base.models import BaseModel

class Wallet(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    balance = models.BigIntegerField(default=0)

    objects = WalletManager()

    def deposit(self, amount: int):
        # todo: deposit the amount into this wallet
        pass

    def __str__(self):
        return self.uuid

class Transaction(BaseModel):
    amount = models.BigIntegerField()
    uuid = models.ForeignKey(Wallet,on_delete=models.CASCADE)
    is_withdrawal = models.BooleanField(default=False)

    objects = TransactionManager()

    def __str__(self):
        return f"{'Withdrawal' if self.is_withdrawal else 'Deposit'} of {self.amount} for {self.wallet.uuid}"


