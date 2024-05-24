from django.contrib import admin
from wallets.models import Wallet, Transaction, ScheduledWithdrawal

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Wallet model.

    This class defines the display options, search fields, and read-only fields for the Wallet model
    in the Django admin interface. It specifies which fields will be shown in the list display,
    which fields can be searched, and which fields are read-only.

    Attributes:
        list_display (tuple): A tuple of field names to display in the list view.
            - 'uuid': The unique identifier for the wallet.
            - 'balance': The current balance of the wallet.
            - 'updated_at': The timestamp when the wallet was last updated.
            - 'created_at': The timestamp when the wallet was created.

        search_fields (tuple): A tuple of field names to use for the search functionality.
            - 'uuid': Allows searching by the unique identifier of the wallet.

        readonly_fields (tuple): A tuple of field names that will be read-only in the admin interface.
            - 'uuid': The unique identifier for the wallet, which cannot be modified.
    """
    list_display = ('uuid', 'balance','updated_at','created_at')
    search_fields = ('uuid',)
    readonly_fields = ('uuid',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Transaction model.

    This class defines the display options and filters for the Transaction model
    in the Django admin interface. It specifies which fields will be shown in 
    the list display and which fields can be used to filter the transactions.

    Attributes:
        list_display (tuple): A tuple of field names to display in the list view.
            - 'wallet': The wallet associated with the transaction.
            - 'amount': The amount of the transaction.
            - 'is_withdrawal': Indicates if the transaction is a withdrawal.
            - 'settle': Indicates if the transaction has been settled.
            - 'bank_status_code': The status code from the bank related to the transaction.
            - 'bank_message': The message from the bank related to the transaction.
            - 'created_at': The timestamp when the transaction was created.

        list_filter (tuple): A tuple of field names to filter the transactions in the list view.
            - 'is_withdrawal': Filters the transactions based on whether they are withdrawals.
    """
    list_display = ('wallet','amount', 'is_withdrawal','settle','bank_status_code','bank_message','created_at')
    list_filter = ('is_withdrawal',)

@admin.register(ScheduledWithdrawal)
class ScheduledWithdrawalAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ScheduledWithdrawal model.

    This class defines the display options for the ScheduledWithdrawal model
    in the Django admin interface. It specifies which fields will be shown
    in the list display.

    Attributes:
        list_display (tuple): A tuple of field names to display in the list view.
            - 'wallet': The wallet associated with the scheduled withdrawal.
            - 'amount': The amount of the scheduled withdrawal.
            - 'processed': Whether the scheduled withdrawal has been processed.
    """
    list_display = ('wallet', 'amount', 'processed')