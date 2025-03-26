import datetime
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory

from core.domain.feedback import Feedback
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.mongo_feedback import MongoFeedbackStorage


@pytest.fixture(scope="function")
def feedback_storage(storage: MongoStorage) -> MongoFeedbackStorage:
    return storage.feedback


class TestStoreFeedback:
    async def test_store_feedback_success(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Create a feedback object
        feedback = Feedback(
            outcome="positive",
            comment="Great job!",
            user_id="user123",
            run_id="run123",
        )

        # Store the feedback
        stored_feedback = await feedback_storage.store_feedback(1, 1, feedback)

        # Verify the stored feedback
        assert stored_feedback.outcome == "positive"
        assert stored_feedback.comment == "Great job!"
        assert stored_feedback.user_id == "user123"
        assert stored_feedback.run_id == "run123"
        assert stored_feedback.id is not None

        # Verify in database
        doc = await feedback_col.find_one({"tenant_uid": 1})
        assert doc is not None
        assert doc["outcome"] == "positive"
        assert doc["comment"] == "Great job!"
        assert doc["user_id"] == "user123"
        assert doc["run_id"] == "run123"
        assert doc["is_stale"] is False
        assert str(doc["_id"]) == stored_feedback.id

    async def test_store_feedback_empty_user_id(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Create a feedback object with empty user_id
        feedback = Feedback(
            outcome="positive",
            comment="Great job!",
            user_id=None,
            run_id="run123",
        )

        # Store the feedback
        stored_feedback = await feedback_storage.store_feedback(1, 1, feedback)

        # Verify the stored feedback
        assert stored_feedback.outcome == "positive"
        assert stored_feedback.comment == "Great job!"
        assert stored_feedback.user_id is None
        assert stored_feedback.run_id == "run123"

        # Verify in database
        doc = await feedback_col.find_one({"tenant_uid": 1})
        assert doc is not None
        assert doc["outcome"] == "positive"
        assert doc["comment"] == "Great job!"
        assert doc["user_id"] == ""
        assert doc["run_id"] == "run123"
        assert doc["is_stale"] is False

    async def test_store_feedback_makes_existing_stale(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Create and store initial feedback
        initial_feedback = Feedback(
            outcome="positive",
            comment="Initial feedback",
            user_id="user123",
            run_id="run123",
        )
        await feedback_storage.store_feedback(1, 1, initial_feedback)

        # Create and store new feedback for same user and run
        new_feedback = Feedback(
            outcome="negative",
            comment="New feedback",
            user_id="user123",
            run_id="run123",
        )
        await feedback_storage.store_feedback(1, 1, new_feedback)

        # Verify both feedbacks exist in database
        cursor = feedback_col.find({"tenant_uid": 1})
        docs: list[dict[str, Any]] = [d async for d in cursor]
        assert len(docs) == 2

        # Find the initial feedback
        initial_doc = next(doc for doc in docs if doc["comment"] == "Initial feedback")
        assert initial_doc["is_stale"] is True

        # Find the new feedback
        new_doc = next(doc for doc in docs if doc["comment"] == "New feedback")
        assert new_doc["is_stale"] is False
        assert new_doc["outcome"] == "negative"

    async def test_store_feedback_different_users(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Create and store feedback for first user
        feedback1 = Feedback(
            outcome="positive",
            comment="User 1 feedback",
            user_id="user1",
            run_id="run123",
        )
        await feedback_storage.store_feedback(1, 1, feedback1)

        # Create and store feedback for second user
        feedback2 = Feedback(
            outcome="negative",
            comment="User 2 feedback",
            user_id="user2",
            run_id="run123",
        )
        await feedback_storage.store_feedback(1, 1, feedback2)

        # Verify both feedbacks exist and are not stale
        cursor = feedback_col.find({"tenant_uid": 1})
        docs: list[dict[str, Any]] = [d async for d in cursor]
        assert len(docs) == 2

        # Find feedback for user1
        user1_doc = next(doc for doc in docs if doc["user_id"] == "user1")
        assert user1_doc["is_stale"] is False
        assert user1_doc["comment"] == "User 1 feedback"

        # Find feedback for user2
        user2_doc = next(doc for doc in docs if doc["user_id"] == "user2")
        assert user2_doc["is_stale"] is False
        assert user2_doc["comment"] == "User 2 feedback"

    async def test_store_feedback_different_runs(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Create and store feedback for first run
        feedback1 = Feedback(
            outcome="positive",
            comment="Run 1 feedback",
            user_id="user123",
            run_id="run1",
        )
        await feedback_storage.store_feedback(1, 1, feedback1)

        # Create and store feedback for second run
        feedback2 = Feedback(
            outcome="negative",
            comment="Run 2 feedback",
            user_id="user123",
            run_id="run2",
        )
        await feedback_storage.store_feedback(1, 1, feedback2)

        # Verify both feedbacks exist and are not stale
        cursor = feedback_col.find({"tenant_uid": 1})
        docs = [d async for d in cursor]

        assert len(docs) == 2

        # Find feedback for run1
        run1_doc = next(doc for doc in docs if doc["run_id"] == "run1")
        assert run1_doc["is_stale"] is False
        assert run1_doc["comment"] == "Run 1 feedback"

        # Find feedback for run2
        run2_doc = next(doc for doc in docs if doc["run_id"] == "run2")
        assert run2_doc["is_stale"] is False
        assert run2_doc["comment"] == "Run 2 feedback"


class TestGetFeedback:
    async def test_get_feedback_success(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Create and store feedback
        feedback = Feedback(
            outcome="positive",
            comment="Great job!",
            user_id="user123",
            run_id="run123",
        )
        await feedback_storage.store_feedback(1, 1, feedback)

        # Retrieve the feedback
        retrieved_feedback = await feedback_storage.get_feedback(1, 1, "run123", "user123")

        # Verify the retrieved feedback
        assert retrieved_feedback is not None
        assert retrieved_feedback.outcome == "positive"
        assert retrieved_feedback.comment == "Great job!"

    async def test_get_feedback_not_found(
        self,
        feedback_storage: MongoFeedbackStorage,
    ) -> None:
        # Try to retrieve non-existent feedback
        retrieved_feedback = await feedback_storage.get_feedback(1, 1, "nonexistent", "user123")
        assert retrieved_feedback is None

    async def test_get_feedback_empty_user_id(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Create and store feedback with empty user_id
        feedback = Feedback(
            outcome="positive",
            comment="Great job!",
            user_id=None,
            run_id="run123",
        )
        await feedback_storage.store_feedback(1, 1, feedback)

        # Retrieve the feedback with None user_id
        retrieved_feedback = await feedback_storage.get_feedback(1, 1, "run123", None)

        # Verify the retrieved feedback
        assert retrieved_feedback is not None
        assert retrieved_feedback.outcome == "positive"
        assert retrieved_feedback.comment == "Great job!"

    async def test_get_feedback_stale_feedback(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Create and store initial feedback
        initial_feedback = Feedback(
            outcome="positive",
            comment="Initial feedback",
            user_id="user123",
            run_id="run123",
        )
        await feedback_storage.store_feedback(1, 1, initial_feedback)

        # Create and store new feedback to make initial feedback stale
        new_feedback = Feedback(
            outcome="negative",
            comment="New feedback",
            user_id="user123",
            run_id="run123",
        )
        await feedback_storage.store_feedback(1, 1, new_feedback)

        # Try to retrieve the stale feedback
        retrieved_feedback = await feedback_storage.get_feedback(1, 1, "run123", "user123")

        # Verify we get the new feedback, not the stale one
        assert retrieved_feedback is not None
        assert retrieved_feedback.outcome == "negative"
        assert retrieved_feedback.comment == "New feedback"


class TestListFeedback:
    async def test_list_feedback_empty(
        self,
        feedback_storage: MongoFeedbackStorage,
    ) -> None:
        # Test listing feedback when no feedback exists
        feedback_list = [feedback async for feedback in feedback_storage.list_feedback(1, None)]
        assert len(feedback_list) == 0

    async def test_list_feedback_multiple_entries(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
        frozen_time: FrozenDateTimeFactory,
    ) -> None:
        # Create and store multiple feedback entries
        feedback1 = Feedback(
            outcome="positive",
            comment="First feedback",
            user_id="user1",
            run_id="run1",
        )
        feedback2 = Feedback(
            outcome="negative",
            comment="Second feedback",
            user_id="user2",
            run_id="run1",
        )
        feedback3 = Feedback(
            outcome="positive",
            comment="Third feedback",
            user_id="user3",
            run_id="run2",
        )

        await feedback_storage.store_feedback(1, 1, feedback1)
        frozen_time.tick(delta=datetime.timedelta(seconds=1))
        await feedback_storage.store_feedback(1, 1, feedback2)
        frozen_time.tick(delta=datetime.timedelta(seconds=1))
        await feedback_storage.store_feedback(1, 1, feedback3)

        # List all feedback for task_uid=1
        feedback_list = [feedback async for feedback in feedback_storage.list_feedback(1, None)]
        assert len(feedback_list) == 3

        # Verify feedback is sorted by _id in descending order (most recent first)
        assert feedback_list[0].comment == "Third feedback"
        assert feedback_list[1].comment == "Second feedback"
        assert feedback_list[2].comment == "First feedback"

    async def test_list_feedback_with_run_id_filter(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Create and store feedback for different runs
        feedback1 = Feedback(
            outcome="positive",
            comment="Run 1 feedback",
            user_id="user1",
            run_id="run1",
        )
        feedback2 = Feedback(
            outcome="negative",
            comment="Run 2 feedback",
            user_id="user2",
            run_id="run2",
        )

        await feedback_storage.store_feedback(1, 1, feedback1)
        await feedback_storage.store_feedback(1, 1, feedback2)

        # List feedback for specific run_id
        feedback_list = [feedback async for feedback in feedback_storage.list_feedback(1, "run1")]
        assert len(feedback_list) == 1
        assert feedback_list[0].comment == "Run 1 feedback"
        assert feedback_list[0].run_id == "run1"

    async def test_list_feedback_excludes_stale(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Create initial feedback that will become stale
        initial_feedback = Feedback(
            outcome="positive",
            comment="Initial feedback",
            user_id="user1",
            run_id="run1",
        )
        await feedback_storage.store_feedback(1, 1, initial_feedback)

        # Create new feedback that makes the initial one stale
        updated_feedback = Feedback(
            outcome="negative",
            comment="Updated feedback",
            user_id="user1",
            run_id="run1",
        )
        await feedback_storage.store_feedback(1, 1, updated_feedback)

        # List feedback
        feedback_list = [feedback async for feedback in feedback_storage.list_feedback(1, "run1")]
        assert len(feedback_list) == 1
        assert feedback_list[0].comment == "Updated feedback"
        assert feedback_list[0].outcome == "negative"

    async def test_list_feedback_different_tasks(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Create feedback for different tasks
        feedback1 = Feedback(
            outcome="positive",
            comment="Task 1 feedback",
            user_id="user1",
            run_id="run1",
        )
        feedback2 = Feedback(
            outcome="negative",
            comment="Task 2 feedback",
            user_id="user1",
            run_id="run1",
        )

        await feedback_storage.store_feedback(1, 1, feedback1)
        await feedback_storage.store_feedback(1, 2, feedback2)

        # List feedback for task_uid=1
        task1_feedback = [feedback async for feedback in feedback_storage.list_feedback(1, None)]
        assert len(task1_feedback) == 1
        assert task1_feedback[0].comment == "Task 1 feedback"

        # List feedback for task_uid=2
        task2_feedback = [feedback async for feedback in feedback_storage.list_feedback(2, None)]
        assert len(task2_feedback) == 1
        assert task2_feedback[0].comment == "Task 2 feedback"


class TestCountFeedback:
    async def test_count_feedback_scenarios(
        self,
        feedback_storage: MongoFeedbackStorage,
        feedback_col: AsyncCollection,
    ) -> None:
        # Initially should be empty
        count = await feedback_storage.count_feedback(1, None)
        assert count == 0

        # Create and store multiple feedback entries
        feedback1 = Feedback(
            outcome="positive",
            comment="First feedback",
            user_id="user1",
            run_id="run1",
        )
        feedback2 = Feedback(
            outcome="negative",
            comment="Second feedback",
            user_id="user2",
            run_id="run1",
        )
        feedback3 = Feedback(
            outcome="positive",
            comment="Third feedback",
            user_id="user3",
            run_id="run2",
        )

        await feedback_storage.store_feedback(1, 1, feedback1)
        await feedback_storage.store_feedback(1, 1, feedback2)
        await feedback_storage.store_feedback(1, 1, feedback3)

        # Count all feedback for task_uid=1
        count = await feedback_storage.count_feedback(1, None)
        assert count == 3

        # Count feedback for specific run_id
        count_run1 = await feedback_storage.count_feedback(1, "run1")
        assert count_run1 == 2

        # Make one feedback stale
        stale_feedback = Feedback(
            outcome="negative",
            comment="Updated feedback",
            user_id="user1",
            run_id="run1",
        )
        await feedback_storage.store_feedback(1, 1, stale_feedback)

        # Count should exclude stale feedback
        count_run1_after_stale = await feedback_storage.count_feedback(1, "run1")
        assert count_run1_after_stale == 2
