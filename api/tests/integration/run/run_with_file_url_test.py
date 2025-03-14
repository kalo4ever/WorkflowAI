from tests.integration.common import (
    IntegrationTestClient,
)


async def test_run_with_file_url(test_client: IntegrationTestClient):
    task = await test_client.create_task(
        input_schema={
            "type": "object",
            "properties": {
                "image": {
                    "$ref": "#/$defs/Image",
                },
            },
            "required": ["image"],
        },
    )

    assert "url" in task["input_schema"]["json_schema"]["$defs"]["Image"]["properties"]

    test_client.mock_openai_call()

    test_client.httpx_mock.add_response(
        url="https://bla.com/image.png",
        method="GET",
        status_code=200,
        content=b"fhefheziuhfzeuihfeuizhfuezh",
    )

    task_run = await test_client.run_task_v1(
        task=task,
        task_input={"image": {"url": "https://bla.com/image.png"}},
    )

    await test_client.wait_for_completed_tasks()
    fetched_task_run = await test_client.fetch_run(task, run_id=task_run["id"])

    assert fetched_task_run["task_input"] == {
        "image": {
            "url": "https://bla.com/image.png",
            "content_type": "image/png",
            "storage_url": test_client.storage_url(
                task,
                "b59dccc6e7a926dabccc2f230503ef19dfe4be5634ad5a471d66c1646cd0a1a0.png",
            ),
        },
    }
