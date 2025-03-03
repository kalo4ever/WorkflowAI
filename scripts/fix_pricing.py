from typing import Any

from core.domain.llm_completion import LLMCompletion
from core.domain.llm_usage import LLMUsage
from core.domain.models import Model, Provider
from core.providers.factory.local_provider_factory import LocalProviderFactory
from core.storage.mongo.models.task_group import TaskGroupDocument
from core.storage.mongo.models.task_run_document import TaskRunDocument
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.utils import dump_model
from core.utils import no_op


# TODO: this script assumes that the version has a fixed provider which is no longer likely
async def _compute_pricing_for_run(run: TaskRunDocument) -> tuple[float, list[TaskRunDocument.LLMCompletion]] | None:
    if not run.llm_completions:
        return None

    assert run.group and run.group.properties

    provider = Provider(run.group.properties["provider"])
    provider_cls = LocalProviderFactory.PROVIDER_TYPES[provider]

    model = Model(run.group.properties["model"])

    found_diff = False

    for completion in run.llm_completions:
        usage = await provider_cls().compute_llm_completion_usage(
            model=model,
            completion=LLMCompletion(
                provider=provider,
                messages=completion.messages or [],
                response=completion.response,
                usage=completion.usage or LLMUsage(),
            ),
        )

        if usage != completion.usage:
            completion.usage = usage
            found_diff = True

    if not found_diff:
        return None

    total_cost = float(sum(c.usage.cost_usd for c in run.llm_completions if c.usage and c.usage.cost_usd))
    return total_cost, run.llm_completions


async def _update_pricing_for_run(run: TaskRunDocument, storage: MongoStorage):
    new_pricing = await _compute_pricing_for_run(run)
    if not new_pricing:
        return False

    cost_usd, llm_completions = new_pricing

    print(f"Updating usage for run {run.id}: {run.cost_usd} -> {cost_usd}")  # noqa: T201
    await storage._task_runs_collection.update_one(  # pyright: ignore [reportPrivateUsage]
        {"_id": run.id},
        {"$set": {"cost_usd": cost_usd, "llm_completions": [dump_model(c) for c in llm_completions]}},
    )

    assert run.task

    await storage._task_benchmarks_collection.update_many(  # pyright: ignore [reportPrivateUsage]
        {
            "task_id": run.task.id,
            "task_schema_id": run.task.schema_id,
            "tenant": run.tenant,
            "by_input.by_group.task_run_id": run.id,
        },
        update={"$set": {"by_input.$[i].by_group.$[g].cost_usd": cost_usd}},
        array_filters=[
            {"i.task_input_hash": run.task_input_hash},
            {"g.task_run_id": run.id},
        ],
    )

    return True


async def _recompute_pricing_for_group(group: TaskGroupDocument, storage: MongoStorage, max_updates: int | None):
    task_runs = storage._task_runs_collection  # pyright: ignore [reportPrivateUsage]

    run_filter = {
        "tenant": group.tenant,
        "task.id": group.task_id,
        "task.schema_id": group.task_schema_id,
        "group.hash": group.hash,
    }

    count = 0
    async for run in task_runs.find(run_filter):
        updated = await _update_pricing_for_run(TaskRunDocument.model_validate(run), storage)
        if not updated:
            continue
        count += 1

        if max_updates and count >= max_updates:
            break

    return count


async def fix_pricing_for_groups(storage: MongoStorage, filter: dict[str, Any], max_run_updates: int | None):
    groups = storage._task_run_group_collection  # pyright: ignore [reportPrivateUsage]

    task_groups_using_gemini = [TaskGroupDocument.model_validate(g) async for g in groups.find(filter)]

    print(f"Found {len(task_groups_using_gemini)} task groups using gemini")  # noqa: T201

    total_count = 0
    for group in task_groups_using_gemini:
        model = group.properties.get("model") if group.properties else None
        if not model:
            print(f"Skipping {group.task_id}/{group.task_schema_id}#{group.iteration} as it has no model")  # noqa: T201
            continue
        print(f"Updating {group.task_id}/{group.task_schema_id}#{group.iteration} using {model}")  # noqa: T201
        max_for_group = max_run_updates - total_count if max_run_updates else None
        count = await _recompute_pricing_for_group(group, storage, max_for_group)
        print(f"Updated {count} runs")  # noqa: T201
        total_count += count
        if max_run_updates and total_count >= max_run_updates:
            break


if __name__ == "__main__":
    import asyncio

    from dotenv import load_dotenv

    load_dotenv(override=True)

    storage = MongoStorage(tenant="", encryption=no_op.NoopEncryption(), event_router=no_op.event_router)

    asyncio.run(
        fix_pricing_for_groups(storage, filter={"properties.model": {"$regex": "gemini"}}, max_run_updates=None),
    )
