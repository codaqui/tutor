from django.urls import path
from wallet import views
from wallet.apps import WalletConfig 

app_name = WalletConfig.name

urlpatterns = [
    path('wallet_profile/', views.history_profile, name='wallet_profile'),
]
