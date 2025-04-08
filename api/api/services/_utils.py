import logging
from collections.abc import Sequence

from core.domain.agent_run import AgentRunBase
from core.storage.reviews_storage import ReviewsStorage


# TODO[test]: add dedicated tests, for not it is tested through the runs service
async def apply_reviews(
    storage: ReviewsStorage,
    task_id: str | None,
    runs: Sequence[AgentRunBase],
    logger: logging.Logger,
):
    """Retrieve corresponding reviews for runs and assign them"""
    if not task_id:
        logger.warning("No task id provided, skipping reviews assignment")
        return

    by_eval_hashes: dict[str, list[AgentRunBase]] = {}
    for run in runs:
        by_eval_hashes.setdefault(run.eval_hash, []).append(run)

    async for r in storage.reviews_for_eval_hashes(
        task_id,
        by_eval_hashes.keys(),
    ):
        for run in by_eval_hashes[r.eval_hash]:
            run.assign_review(r)
