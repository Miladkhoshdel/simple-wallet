from celery import shared_task
from wallets.models import ScheduledWithdrawal, Transaction
from django.utils import timezone
from decimal import Decimal
from django.db import models, transaction
import requests
from base.exceptions import BankException
from requests.exceptions import HTTPError, ConnectionError, Timeout


@shared_task
def process_withdrawal(scheduled_withdrawal_id):

    scheduled_withdrawal = ScheduledWithdrawal.objects.get(id=scheduled_withdrawal_id)
    wallet = scheduled_withdrawal.wallet
    
    if scheduled_withdrawal.processed:
        return
    
    try:
        with transaction.atomic():
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
                wallet.deposit(scheduled_withdrawal.amount)
                status_code = 500
                status_response = "HTTP Error."
                settle=False
            except ConnectionError as conn_err:
                wallet.deposit(scheduled_withdrawal.amount)
                status_code = 503
                status_response = "Service unavailable."
                settle=False
            except Timeout as timeout_err:
                wallet.deposit(scheduled_withdrawal.amount)
                status_code = 408
                status_response = "Request Timeout"
                settle=False
            except Exception as e:
                wallet.deposit(scheduled_withdrawal.amount)
                settle=False
            finally:
                transaction_log = Transaction.objects.create(
                    wallet=wallet,
                    amount=scheduled_withdrawal.amount,
                    is_withdrawal=True,
                    settle=settle,
                    bank_status_code = status_code,
                    bank_message = status_response
                )
                return f"Success Processed withdrawal of {scheduled_withdrawal.amount} for {wallet.uuid}"

                
    except Exception as e:
        with transaction.atomic():
            wallet.deposit(scheduled_withdrawal.amount)
            transaction_log = Transaction.objects.create(
                    wallet=wallet,
                    amount=scheduled_withdrawal.amount,
                    is_withdrawal=True,
                    settle=False
                )
            return f"Failed Processed withdrawal of {scheduled_withdrawal.amount} for {wallet.uuid}"

        

    finally:
        scheduled_withdrawal.processed = True
        scheduled_withdrawal.save()
        return f"Success Processed withdrawal of {scheduled_withdrawal.amount} for {wallet.uuid}"
    
