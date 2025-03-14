import logging
import os
from typing import Annotated

from fastapi import Depends, HTTPException

from api.dependencies.security import URLPublicOrganizationDep, UserOrganizationDep
from core.storage import TenantTuple

_logger = logging.getLogger(__name__)
_BLOCK_RUN_FOR_NO_CREDITS = os.getenv("BLOCK_RUN_FOR_NO_CREDITS", "false").lower() == "true"


def check_enough_credits(org_settings: UserOrganizationDep):
    if org_settings is None:
        _logger.warning("User organization settings are None while trying run_schema")
    elif _BLOCK_RUN_FOR_NO_CREDITS and org_settings.current_credits_usd < 0:
        raise HTTPException(status_code=402, detail="Insufficient credits to run the task")
    return org_settings


UserOrganizationHasCreditsDep = Annotated[UserOrganizationDep, Depends(check_enough_credits)]


def author_tenant(org_settings: UserOrganizationHasCreditsDep, url_public_org: URLPublicOrganizationDep):
    # author_tenant is only set if the owner of the task and the current logged in user
    # are different. This is used to determine if the run should be counted towards the
    # user's credits.
    if url_public_org and org_settings and url_public_org.tenant != org_settings.tenant:
        return (org_settings.tenant, org_settings.uid)
    return None


AuthorTenantDep = Annotated[TenantTuple | None, Depends(author_tenant)]
