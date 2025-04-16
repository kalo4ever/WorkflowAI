from core.storage.backend_storage import BackendStorage


class CustomerService:
    def __init__(self, storage: BackendStorage):
        self.storage = storage

    async def handle_customer_created(self):
        pass

    async def handle_customer_migrated(self, from_user_id: str | None, from_anon_id: str | None):
        pass
