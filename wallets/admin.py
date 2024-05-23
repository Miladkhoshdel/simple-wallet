from django.contrib import admin
from wallets.models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'balance')
    search_fields = ('uuid',)
    readonly_fields = ('uuid',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('amount', 'is_withdrawal')
    list_filter = ('is_withdrawal',)