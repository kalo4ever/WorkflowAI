from typing import override

from core.services.emails.email_service import EmailService


class PostmarkService(EmailService):
    def __init__(self):
        pass

    @override
    async def send_payment_failure_email(self, tenant: str) -> None:
        pass
