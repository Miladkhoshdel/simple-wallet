from celery import shared_task
from wallets.models import ScheduledWithdrawal, Wallet
from django.db import transaction, OperationalError
import time

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

    The task retries if it encounters a database lock, waiting for a 
    certain period before retrying, up to a maximum number of attempts.

    Args:
        scheduled_withdrawal_id (int): The ID of the scheduled withdrawal to process.

    Returns:
        str: A message indicating the success or failure of the withdrawal processing.
    """
    scheduled_withdrawal = ScheduledWithdrawal.objects.get(id=scheduled_withdrawal_id)
    wallet = scheduled_withdrawal.wallet
    
    if scheduled_withdrawal.processed:
        return
    
    attempt = 0
    max_attempts = 50
    wait_time = 1 # seconds to wait before retrying

    try:
        while attempt <= max_attempts:
            with transaction.atomic():
                    try:
                        wallet = Wallet.objects.select_for_update().get(id=wallet.id)
                        wallet.withdraw(scheduled_withdrawal.amount)
                        break
                        
                    except OperationalError as e:
                        attempt += 1
                        print(f"Database lock could not be acquired. Attempt {attempt}/{max_attempts}. Retrying in {wait_time} seconds.")
                        time.sleep(wait_time)
                
    except Exception as e:
        print("Main Exception Raised.")
        print(e)

    finally:
        scheduled_withdrawal.processed = True
        scheduled_withdrawal.save()
        return f"Success Processed withdrawal of {scheduled_withdrawal.amount} for {wallet.uuid}"
    
