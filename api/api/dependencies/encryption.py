from typing import Annotated

from fastapi import Depends

from api.services.storage import shared_encryption
from core.utils.encryption import Encryption


def encryption_dependency() -> Encryption:
    return shared_encryption()


EncryptionDep = Annotated[Encryption, Depends(encryption_dependency)]
