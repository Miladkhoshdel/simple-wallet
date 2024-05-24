from django.urls import path

from wallets.views import CreateDepositView, ScheduleWithdrawView, CreateWalletView, RetrieveWalletView, CreateWithdrawView

urlpatterns = [
    path("", CreateWalletView.as_view()),
    path("<uuid>/", RetrieveWalletView.as_view()),
    path("<uuid>/deposit", CreateDepositView.as_view()),
    path("<uuid>/withdraw", CreateWithdrawView.as_view()),
    path("<uuid>/schedulewithdraw", ScheduleWithdrawView.as_view()),
]
