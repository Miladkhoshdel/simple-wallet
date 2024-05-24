import uuid

from django.db import models, transaction
from wallets.managers import WalletManager, TransactionManager, ScheduledWithdrawalManager
from base.models import BaseModel
from decimal import Decimal
from base.exceptions import InsufficientFundsError, BankException
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout

class Wallet(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    balance = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    objects = WalletManager()

    def deposit(self, amount: Decimal):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        try:
            with transaction.atomic():
                self.balance = models.F('balance') + amount
                self.save(update_fields=['balance','updated_at'])
                transaction_log = Transaction.objects.create(
                    wallet=self,
                    amount=amount,
                    is_withdrawal=False,
                    settle=True
                )
                self.refresh_from_db()
        except Exception as e:
            with transaction.atomic():
                transaction_log = Transaction.objects.create(
                        wallet=self,
                        amount=amount,
                        is_withdrawal=False,
                        settle=True
                    )

    def schadule_withdraw(self, amount: Decimal):
        balance = self.balance
        if amount <= Decimal('0'):
            raise ValueError("Withdraw amount must be positive.")
        elif balance < amount:
            raise InsufficientFundsError("Insufficient funds.")
        
        try:
            with transaction.atomic():
                self.balance = models.F('balance') - amount
                self.save(update_fields=['balance','updated_at'])
        except Exception as e:
            print(e)

    def withdraw(self, amount: Decimal):
        balance = self.balance
        if amount <= Decimal('0'):
            raise ValueError("Withdraw amount must be positive.")
        elif balance < amount:
            raise InsufficientFundsError("Insufficient funds.")

        try:
            with transaction.atomic():
                self.balance = models.F('balance') - amount
                self.save(update_fields=['balance','updated_at'])
                try:
                    bank_response = requests.post('http://localhost:8010', timeout=5)
                    bank_response.raise_for_status()
                    json_response = bank_response.json()
                    status_code = json_response.get("status", "-")
                    status_response = json_response.get("data","-")
                    settle=True
                    if status_code != 200:
                        raise BankException("Bank Status code not equal to 200 raised.")
                except HTTPError as http_err:
                    self.balance = models.F('balance') + amount
                    self.save(update_fields=['balance','updated_at'])
                    status_code = 500
                    status_response = "HTTP Error."
                    settle=False
                except ConnectionError as conn_err:
                    self.balance = models.F('balance') + amount
                    self.save(update_fields=['balance','updated_at'])
                    status_code = 503
                    status_response = "Service unavailable."
                    settle=False
                except Timeout as timeout_err:
                    self.balance = models.F('balance') + amount
                    self.save(update_fields=['balance','updated_at'])
                    status_code = 408
                    status_response = "Request Timeout"
                    settle=False
                except Exception as e:
                    self.balance = models.F('balance') + amount
                    self.save(update_fields=['balance','updated_at'])
                    settle=False
                finally:
                    transaction_log = Transaction.objects.create(
                        wallet=self,
                        amount=amount,
                        is_withdrawal=True,
                        settle=settle,
                        bank_status_code = status_code,
                        bank_message = status_response
                    )
                    self.refresh_from_db()
                
        except Exception as e:
            with transaction.atomic():
                transaction_log = Transaction.objects.create(
                        wallet=self,
                        amount=amount,
                        is_withdrawal=True,
                        settle=False
                    )

    def __str__(self):
        return f"{str(self.uuid)}"

class Transaction(BaseModel):
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE)
    is_withdrawal = models.BooleanField(default=False)
    settle = models.BooleanField(default=False)
    bank_status_code = models.CharField(max_length=5, blank=True, null=True)
    bank_message = models.CharField(max_length=10, blank=True, null=True)

    objects = TransactionManager()

    def __str__(self):
        return f"{'Withdrawal' if self.is_withdrawal else 'Deposit'} of {self.amount} for {self.wallet.uuid}"

class ScheduledWithdrawal(BaseModel):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    scheduled_time = models.DateTimeField()
    processed = models.BooleanField(default=False)

    objects = ScheduledWithdrawalManager()

    def __str__(self):
        return f"Scheduled Withdrawal of {self.amount} for {self.wallet.uuid} at {self.scheduled_time}"
