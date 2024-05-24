from django.urls import path

from wallets.views import CreateDepositView, ScheduleWithdrawView, CreateWalletView, RetrieveWalletView, CreateWithdrawView

app_name = "wallets"

urlpatterns = [
    path("", CreateWalletView.as_view(), name="create_wallet"),
    path("<uuid>/", RetrieveWalletView.as_view(), name="retrieve_wallet"),
    path("<uuid>/deposit", CreateDepositView.as_view(), name="create_deposit"),
    path("<uuid>/withdraw", CreateWithdrawView.as_view(), name="create_withdraw"),
    path("<uuid>/schedulewithdraw", ScheduleWithdrawView.as_view(), name="schedule_withdraw"),
]