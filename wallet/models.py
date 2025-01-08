from decimal import Decimal

from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from codaqui.settings import AUTH_USER_MODEL
from utils.models import AuditModel

# Create your models here.


class Activities(AuditModel):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    value = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=255)

    def __str__(self):
        return str(self.value)


class Wallet(AuditModel):
    user = models.OneToOneField(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __str__(self):
        return str(self.balance)

    def credit(self, value: Decimal):
        if type(value) != Decimal:
            value = Decimal(value)
        if type(self.balance) != Decimal:
            self.balance = Decimal(self.balance)
        self.balance = self.balance + value
        self.save()

    def debit(self, value: Decimal):
        if type(value) != Decimal:
            value = Decimal(value)
        if type(self.balance) != Decimal:
            self.balance = Decimal(self.balance)
        self.balance = self.balance - value
        self.save()

    @receiver(pre_save, sender=Activities)
    def activities_created(sender, instance, **kwargs):
        wallet = Wallet.objects.select_for_update().get(user=instance.user)
        if instance.value < 0 and wallet.balance < abs(instance.value):
            raise ValueError("Saldo insuficiente")
        wallet.credit(instance.value)

    @receiver(pre_delete, sender=Activities)
    def transaction_deleted(sender, instance, **kwargs):
        wallet = Wallet.objects.get(user=instance.user)
        wallet.debit(instance.value)
