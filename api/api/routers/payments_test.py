import pytest

from api.routers.payments import AutomaticPaymentRequest


class TestAutomaticPaymentRequest:
    def test_opt_out(self):
        """Check that we can opt out"""
        request = AutomaticPaymentRequest(opt_in=False)
        assert request.opt_in is False

    def test_opt_in(self):
        """Check that we can opt in"""
        request = AutomaticPaymentRequest(opt_in=True, threshold=50, balance_to_maintain=100)
        assert request.opt_in is True
        assert request.threshold == 50
        assert request.balance_to_maintain == 100

    def test_threshold_must_be_greater_than_balance_to_maintain(self):
        """Check that we can't set a threshold that is less than the balance to maintain"""
        with pytest.raises(ValueError):
            AutomaticPaymentRequest(opt_in=True, threshold=100, balance_to_maintain=50)

    def test_threshold_and_balance_to_maintain_must_be_none_when_opt_out(self):
        """Check that we can't set a threshold or balance to maintain when we opt out"""
        with pytest.raises(ValueError):
            AutomaticPaymentRequest(opt_in=False, threshold=100, balance_to_maintain=50)

    def test_threshold_and_balance_to_maintain_must_not_be_none_when_opt_in(self):
        """Check that we can't set a threshold or balance to maintain when we opt out"""
        with pytest.raises(ValueError):
            AutomaticPaymentRequest(opt_in=True, threshold=None, balance_to_maintain=50)
