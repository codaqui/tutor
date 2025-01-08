from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from wallet.models import Activities, Wallet

User = get_user_model()


class TestWalletModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.wallet = Wallet.objects.create(user=self.user, balance=100.0)

    def test_wallet_creation(self):
        """Test if the wallet is created successfully"""
        assert self.wallet.balance == 100.0

    def test_wallet_credit(self):
        """Test if the wallet balance updates correctly when credited"""
        self.wallet.credit(50.0)
        assert self.wallet.balance == 150.0

    def test_wallet_debit(self):
        """Test if the wallet balance updates correctly when debited"""
        self.wallet.debit(50.0)
        assert self.wallet.balance == 50.0

    def test_wallet_str(self):
        """Test the string representation of the wallet"""
        assert str(self.wallet) == str(Decimal('100.0'))

    def test_activities_created(self):
        """Test if activities creation updates the wallet balance"""
        activity = Activities.objects.create(
            user=self.user, value=50.0, description="Test Activity"
        )
        wallet = Wallet.objects.get(user=self.user)
        assert wallet.balance == 150.0

    def test_activities_created_insufficient_balance(self):
        """Test if activities creation raises error on insufficient balance"""
        with self.assertRaisesMessage(ValueError, "Saldo insuficiente"):
            Activities.objects.create(
                user=self.user, value=-150.0, description="Test Activity"
            )

    def test_transaction_deleted(self):
        """Test if deleting an activity updates the wallet balance"""
        activity = Activities.objects.create(
            user=self.user, value=50.0, description="Test Activity"
        )
        wallet = Wallet.objects.get(user=self.user)
        assert wallet.balance == 150.0
        activity.delete()
        wallet.refresh_from_db()
        assert wallet.balance == 100.0
