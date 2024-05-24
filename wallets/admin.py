from django.contrib import admin
from wallets.models import Wallet, Transaction, ScheduledWithdrawal

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'balance','updated_at','created_at')
    search_fields = ('uuid',)
    readonly_fields = ('uuid',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet','amount', 'is_withdrawal','settle','bank_status_code','bank_message','created_at')
    list_filter = ('is_withdrawal',)

@admin.register(ScheduledWithdrawal)
class ScheduledWithdrawalAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'processed')