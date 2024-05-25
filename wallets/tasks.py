from celery import shared_task
from wallets.models import ScheduledWithdrawal, Transaction
from django.db import transaction
import requests
from base.exceptions import BankException
from requests.exceptions import HTTPError, ConnectionError, Timeout
from base.vars import BANK_URL

@shared_task
def process_withdrawal(scheduled_withdrawal_id):
    """
    Asynchronous task for processing a scheduled withdrawal.

    This task function is decorated with @shared_task from Celery,
    making it an asynchronous task. It processes a scheduled withdrawal
    by sending a request to the bank API to initiate the withdrawal.
    If the bank response indicates success, the withdrawal amount is
    deducted from the wallet balance and a transaction log is created.
    If an error occurs during the process, the withdrawal amount is
    refunded to the wallet balance and an appropriate transaction log
    is created.

    Args:
        scheduled_withdrawal_id (int): The ID of the scheduled withdrawal to process.

    Returns:
        str: A message indicating the success or failure of the withdrawal processing.
    """
    scheduled_withdrawal = ScheduledWithdrawal.objects.get(id=scheduled_withdrawal_id)
    wallet = scheduled_withdrawal.wallet
    
    if scheduled_withdrawal.processed:
        return
    
    try:
        with transaction.atomic():
            try:
                if wallet.balance >= scheduled_withdrawal.amount:
                    print("sufficient balance")
                    wallet.schadule_withdraw(scheduled_withdrawal.amount)
                    bank_response = requests.post(BANK_URL, timeout=5)
                    bank_response.raise_for_status()
                    json_response = bank_response.json()
                    status_code = json_response.get("status", "-")
                    status_response = json_response.get("data","-")
                    settle=True
                    if status_code != 200:
                        raise BankException("Bank Status code not equal to 200 raised.")
                else:
                    settle=False
                    status_code="-"
                    status_response="-"
                    print("insufficient balance.")
                    return "insufficient balance."
            except HTTPError as http_err:
                print("http_err Exception Raised.")
                wallet.deposit(scheduled_withdrawal.amount)
                status_code = 500
                status_response = "HTTP Error."
                settle=False
            except ConnectionError as conn_err:
                print("conn_err Exception Raised.")
                wallet.deposit(scheduled_withdrawal.amount)
                status_code = 503
                status_response = "Service unavailable."
                settle=False
            except Timeout as timeout_err:
                print("timeout_err Exception Raised.")
                wallet.deposit(scheduled_withdrawal.amount)
                status_code = 408
                status_response = "Request Timeout"
                settle=False
            except Exception as e:
                print("Exception Raised.")
                settle=False
                status_response="-"
                status_response="-"
                wallet.deposit(scheduled_withdrawal.amount)
                settle=False
            finally:
                print("Finally block called.")
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
        print("Main Exception Raised.")
        print(e)

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
    
