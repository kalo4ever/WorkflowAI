import logging

from fastapi import APIRouter
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/llms.txt")
async def get_llms_txt(
    token: str,
) -> FileResponse:
    """
    Get the llms.txt file for the user's organization.
    Returns a downloadable text file containing all the LLM task schemas
    available to the organization.
    """
    # ENDPOINT: GET /llms.txt?token=...
    # If no token is provided, return llms.txt file with just workflowai documentation
    # update security to use token param to authenticate
    # get the user's organization from the token
    # get the storage client for the user
    # Use the tasks and template to build the llms.txt file
    # return the llms.txt file

    # llms_txt_content = await service.build_llms_txt_content(user_org)
    llms_txt_content = "llms_txt_content"
    return FileResponse(llms_txt_content, filename="llms.txt")
