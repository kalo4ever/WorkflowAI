import pytest

from .email_utils import safe_domain_from_email


class TestDomainFromEmail:
    @pytest.mark.parametrize(
        "email,expected_domain",
        [
            ("user@example.com", "example.com"),
            ("test.user@domain.co.uk", "domain.co.uk"),
            ("email+alias@gmail.com", "gmail.com"),
            ("user.name@subdomain.example.org", "subdomain.example.org"),
            ("user@localhost", "localhost"),
            ("user@127.0.0.1", "127.0.0.1"),
            ("user", None),
            ("", None),
            ("user@", None),
            ("@domain.com", "domain.com"),
            (None, None),
        ],
    )
    def test_safe_domain_from_email(self, email: str, expected_domain: str) -> None:
        """Test that domain is correctly extracted from valid email addresses."""
        assert safe_domain_from_email(email) == expected_domain
