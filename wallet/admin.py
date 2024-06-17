from django.contrib import admin
from wallet.models import Activities, Wallet

# Register your models here.

class ActivitiesAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'description')

class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')

admin.site.register(Activities, ActivitiesAdmin)
admin.site.register(Wallet, WalletAdmin)