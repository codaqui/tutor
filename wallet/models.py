from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from utils.models import AuditModel
from codaqui.settings import AUTH_USER_MODEL

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
        related_name='wallet',
    )
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __str__(self):
        return str(self.balance)

    def credit(self, value):
        self.balance += value
        self.save()

    def debit(self, value):
        self.balance -= value
        self.save()


    @receiver(pre_save, sender=Activities)
    def activities_created(sender, instance, **kwargs):
        wallet = Wallet.objects.select_for_update().get(user=instance.user)
        if instance.value < 0 and wallet.balance < abs(instance.value):
            raise ValueError('Saldo insuficiente')
        wallet.credit(instance.value)

    @receiver(pre_delete, sender=Activities)
    def transaction_deleted(sender, instance, **kwargs):
        wallet = Wallet.objects.get(user=instance.user)
        wallet.debit(instance.value)
