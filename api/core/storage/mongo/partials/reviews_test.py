from typing import Any, Literal

import pytest
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from core.domain.errors import DuplicateValueError
from core.domain.review import Review, ReviewerType, ReviewOutcome
from core.domain.run_identifier import RunIdentifier
from core.domain.search_query import ReviewSearchOptions
from core.domain.utils import compute_eval_hash
from core.storage import ObjectNotFoundException
from core.storage.mongo.models.pyobjectid import PyObjectID
from core.storage.mongo.models.review_document import ReviewDocument
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.reviews import MongoReviewsStorage
from core.storage.mongo.utils import dump_model
from core.storage.reviews_storage import AIReviewerFilter
from core.utils.dicts import set_at_keypath_str


def _review_doc(
    reviewer_type: ReviewerType = "user",
    task_id: str = "task_id",
    is_stale: bool = False,
    task_input_hash: str = "task_input_hash",
    task_output_hash: str = "task_output_hash",
    id: str | None = None,
    reviewer: ReviewDocument.UserReviewer | ReviewDocument.AIReviewer | None = None,
    status: Literal["in_progress", "completed"] = "completed",
    evaluator_id: str = "evaluator_id",
    eval_hash: str | None = None,
    outcome: ReviewOutcome = "positive",
):
    if reviewer is None:
        if reviewer_type == "user":
            reviewer = ReviewDocument.UserReviewer(user_id="user_id")
        else:
            reviewer = ReviewDocument.AIReviewer(evaluator_id=evaluator_id, input_evaluation_id="input_evaluation_id")

    return ReviewDocument(
        _id=PyObjectID.from_str(id) if id else PyObjectID.new(),
        tenant="test_tenant",
        task_id=task_id,
        task_schema_id=1,
        task_input_hash=task_input_hash,
        task_output_hash=task_output_hash,
        eval_hash=eval_hash or compute_eval_hash(1, task_input_hash, task_output_hash),
        reviewer=reviewer,
        is_stale=is_stale,
        outcome=outcome,
        status=status,
        positive_aspects=["positive_aspects"],
        negative_aspects=["negative_aspects"],
    )


@pytest.fixture()
def reviews_storage(storage: MongoStorage):
    return storage.reviews


class TestMarkAsStale:
    async def test_mark_as_stale(self, reviews_col: AsyncCollection, reviews_storage: MongoReviewsStorage):
        await reviews_col.insert_many(
            [
                dump_model(doc)
                for doc in [
                    _review_doc(id="66568f3c40d79b0d69ece4a8"),  # user review
                    _review_doc(id="66568f3c40d79b0d69ece4a9", reviewer_type="ai"),
                    _review_doc(id="66568f3c40d79b0d69ece4aa", reviewer_type="ai", evaluator_id="e1"),
                ]
            ],
        )

        assert len([d async for d in reviews_col.find({"is_stale": False})]) == 3, "sanity"

        await reviews_storage.mark_as_stale(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="task_input_hash",
            task_output_hash="task_output_hash",
            reviewer_type="ai",
        )

        non_stale = [d async for d in reviews_col.find({"is_stale": False})]
        assert len(non_stale) == 1
        assert str(non_stale[0]["_id"]) == "66568f3c40d79b0d69ece4a8"

    async def test_mark_as_stale_with_before_id(
        self,
        reviews_col: AsyncCollection,
        reviews_storage: MongoReviewsStorage,
    ):
        await reviews_col.insert_many(
            [
                dump_model(doc)
                for doc in [
                    _review_doc(id="66568f3c40d79b0d69ece4a8"),  # user review
                    _review_doc(id="66568f3d40d79b0d69ece4a9", reviewer_type="ai", evaluator_id="e1"),
                    _review_doc(id="66568f3e40d79b0d69ece4aa", reviewer_type="ai", evaluator_id="e2"),
                ]
            ],
        )
        assert len([d async for d in reviews_col.find({"is_stale": False})]) == 3, "sanity"

        await reviews_storage.mark_as_stale(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="task_input_hash",
            task_output_hash="task_output_hash",
            reviewer_type="ai",
            before_id="66568f3e40d79b0d69ece4aa",
        )

        non_stale = sorted([str(d["_id"]) async for d in reviews_col.find({"is_stale": False})])
        assert non_stale == ["66568f3c40d79b0d69ece4a8", "66568f3e40d79b0d69ece4aa"]


class TestInsertReview:
    async def test_insert_review(self, reviews_col: AsyncCollection, reviews_storage: MongoReviewsStorage):
        review = Review(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="task_input_hash",
            task_output_hash="task_output_hash",
            outcome="positive",
            status="completed",
            reviewer=Review.UserReviewer(user_id="user_id", user_email="user_email"),
        )
        created = await reviews_storage.insert_review(review)
        assert created.id != ""
        # created at should be properly set
        assert created.created_at != review.created_at


class TestListReviews:
    async def test_list_reviews(self, reviews_col: AsyncCollection, reviews_storage: MongoReviewsStorage):
        await reviews_col.insert_many(
            [
                dump_model(doc)
                for doc in [
                    _review_doc(id="66568f3c40d79b0d69ece4a8"),  # user review
                    _review_doc(id="66568f3c40d79b0d69ece4a9", reviewer_type="ai", evaluator_id="e1"),
                    _review_doc(id="66568f3c40d79b0d69ece4aa", reviewer_type="ai", is_stale=True, evaluator_id="e2"),
                    _review_doc(id="66568f3c40d79b0d69ece4ab", reviewer_type="ai", is_stale=False, evaluator_id="e3"),
                ]
            ],
        )

        reviews = [
            r.id
            async for r in reviews_storage.list_reviews(
                task_id="task_id",
                task_schema_id=1,
                task_input_hash="task_input_hash",
                task_output_hash="task_output_hash",
            )
        ]
        assert reviews == ["66568f3c40d79b0d69ece4ab", "66568f3c40d79b0d69ece4a9", "66568f3c40d79b0d69ece4a8"]


class TestReviewFlow:
    async def test_flow(self, reviews_storage: MongoReviewsStorage):
        task_kwargs: dict[str, Any] = {
            "task_id": "task_id",
            "task_schema_id": 1,
        }
        kwargs: dict[str, Any] = {
            **task_kwargs,
            "task_input_hash": "input_hash",
            "task_output_hash": "output_hash",
        }

        # insert review
        review = await reviews_storage.insert_review(
            Review(
                outcome="unsure",
                status="completed",
                reviewer=Review.AIReviewer(evaluator_id="evaluator_id", input_evaluation_id="input_evaluation_id"),
                **kwargs,
            ),
        )
        # list reviews
        reviews = [r async for r in reviews_storage.list_reviews(**kwargs)]
        assert len(reviews) == 1
        assert reviews[0].id == review.id
        # get review by id
        review_by_id = await reviews_storage.get_review_by_id(**task_kwargs, review_id=review.id)
        assert review_by_id.id == review.id
        # mark as stale and add user review
        await reviews_storage.mark_as_stale(**kwargs, reviewer_type="ai")
        review_user = await reviews_storage.insert_review(
            Review(
                outcome="unsure",
                status="completed",
                reviewer=Review.UserReviewer(user_id="user_id", user_email="user_email"),
                **kwargs,
            ),
        )
        # list reviews
        reviews = [r async for r in reviews_storage.list_reviews(**kwargs)]
        assert len(reviews) == 1
        assert reviews[0].id == review_user.id

    async def test_in_progress_complete_review(self, reviews_storage: MongoReviewsStorage):
        review = await reviews_storage.insert_in_progress_review(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="task_input_hash",
            task_output_hash="task_output_hash",
            evaluator_id="evaluator_id",
            input_evaluation_id="input_evaluation_id",
        )

        await reviews_storage.complete_review(
            review_id=review.id,
            outcome="positive",
            comment="comment",
            confidence_score=0.5,
            run_identifier=RunIdentifier(tenant="test_tenant", run_id="run_id", task_id="task_id", task_schema_id=1),
            positive_aspects=["positive_aspects"],
            negative_aspects=["negative_aspects"],
        )

        review_by_id = await reviews_storage.get_review_by_id(
            task_id="task_id",
            task_schema_id=1,
            review_id=review.id,
        )

        assert review_by_id == Review(
            id=review.id,
            created_at=review.created_at,
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="task_input_hash",
            task_output_hash="task_output_hash",
            outcome="positive",
            status="completed",
            comment="comment",
            reviewer=Review.AIReviewer(
                evaluator_id="evaluator_id",
                input_evaluation_id="input_evaluation_id",
                confidence_score=0.5,
                run_identifier=RunIdentifier(
                    tenant="test_tenant",
                    run_id="run_id",
                    task_id="task_id",
                    task_schema_id=1,
                ),
            ),
            positive_aspects=["positive_aspects"],
            negative_aspects=["negative_aspects"],
        )

    async def test_add_comment_to_review(self, reviews_storage: MongoReviewsStorage):
        review = await reviews_storage.insert_review(
            Review(
                task_id="task_id",
                task_schema_id=1,
                task_input_hash="task_input_hash",
                task_output_hash="task_output_hash",
                outcome="unsure",
                status="completed",
                reviewer=Review.UserReviewer(user_id="user_id", user_email="user_email"),
            ),
        )
        assert review.comment is None, "sanity"
        await reviews_storage.add_comment_to_review(
            review_id=review.id,
            comment="comment",
            responding_to="66568f3c40d79b0d69ece4a8",
        )

        new_review = await reviews_storage.get_review_by_id(
            task_id="task_id",
            task_schema_id=1,
            review_id=review.id,
        )
        assert new_review.comment == "comment"
        assert new_review.responding_to_review_id == "66568f3c40d79b0d69ece4a8"


class TestGetReviewByHash:
    async def test_get_review_by_hash(self, reviews_col: AsyncCollection, reviews_storage: MongoReviewsStorage):
        await reviews_col.insert_one(dump_model(_review_doc(id="66568f3c40d79b0d69ece4a8")))

        review = await reviews_storage.get_review_by_hash(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="task_input_hash",
            task_output_hash="task_output_hash",
        )
        assert review is not None
        assert review.id == "66568f3c40d79b0d69ece4a8"
        assert review.positive_aspects == ["positive_aspects"]
        assert review.negative_aspects == ["negative_aspects"]

        review = await reviews_storage.get_review_by_hash(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="task_input_hash",
            task_output_hash="task_output_hash_2",
        )
        assert review is None

    async def test_project_fields(self, reviews_col: AsyncCollection, reviews_storage: MongoReviewsStorage):
        await reviews_col.insert_one(dump_model(_review_doc(id="66568f3c40d79b0d69ece4a8")))

        user_review = await reviews_storage.get_review_by_hash(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="task_input_hash",
            task_output_hash="task_output_hash",
            include={"outcome", "status"},
        )
        assert user_review is not None
        assert user_review.id == "66568f3c40d79b0d69ece4a8"
        assert user_review.outcome == "positive"
        assert user_review.status == "completed"
        assert user_review.task_input_hash == ""

    async def test_filter_by_ai_reviewer(self, reviews_col: AsyncCollection, reviews_storage: MongoReviewsStorage):
        await reviews_col.insert_one(dump_model(_review_doc(id="66568f3c40d79b0d69ece4a8", reviewer_type="ai")))

        kwargs: Any = {
            "task_id": "task_id",
            "task_schema_id": 1,
            "task_input_hash": "task_input_hash",
            "task_output_hash": "task_output_hash",
            "include": {"outcome", "status"},
        }

        ai_review = await reviews_storage.get_review_by_hash(**kwargs, reviewer="ai")
        assert ai_review is not None
        assert ai_review.id == "66568f3c40d79b0d69ece4a8"
        assert ai_review.outcome == "positive"
        assert ai_review.status == "completed"

        ai_review = await reviews_storage.get_review_by_hash(
            **kwargs,
            reviewer=AIReviewerFilter(
                evaluator_id="evaluator_id",
                input_evaluation_id="input_evaluation_id",
            ),
        )
        assert ai_review and ai_review.id == "66568f3c40d79b0d69ece4a8"

        ai_review = await reviews_storage.get_review_by_hash(
            **kwargs,
            reviewer=AIReviewerFilter(
                evaluator_id="evaluator_id1",
                input_evaluation_id="input_evaluation_id",
            ),
        )
        assert not ai_review


class TestGetReviewById:
    async def test_get_review_by_id(self, reviews_col: AsyncCollection, reviews_storage: MongoReviewsStorage):
        await reviews_col.insert_one(dump_model(_review_doc(id="66568f3c40d79b0d69ece4a8")))

        review = await reviews_storage.get_review_by_id(
            task_id="task_id",
            task_schema_id=1,
            review_id="66568f3c40d79b0d69ece4a8",
        )
        assert review is not None
        assert review.id == "66568f3c40d79b0d69ece4a8"


class TestInsertInProgressReview:
    async def test_insert_in_progress_review(
        self,
        reviews_storage: MongoReviewsStorage,
        reviews_col: AsyncCollection,
    ):
        review = await reviews_storage.insert_in_progress_review(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="task_input_hash",
            task_output_hash="task_output_hash",
            evaluator_id="evaluator_id",
            input_evaluation_id="input_evaluation_id",
        )
        assert review.id != ""

        doc = await reviews_col.find_one({"_id": ObjectId(review.id)})
        assert doc is not None
        assert doc["eval_hash"] == review.eval_hash

    async def test_insert_in_progress_review_twice(
        self,
        reviews_storage: MongoReviewsStorage,
    ):
        kwargs: dict[str, Any] = {
            "task_id": "task_id",
            "task_schema_id": 1,
            "task_input_hash": "task_input_hash",
            "task_output_hash": "task_output_hash",
        }
        await reviews_storage.insert_in_progress_review(
            **kwargs,
            evaluator_id="evaluator_id",
            input_evaluation_id="input_evaluation_id",
        )

        # I cannot insert with the same evaluator_id and input_evaluation_id
        with pytest.raises(DuplicateValueError):
            await reviews_storage.insert_in_progress_review(
                **kwargs,
                evaluator_id="evaluator_id",
                input_evaluation_id="input_evaluation_id",
            )

        # But otherwise I can
        await reviews_storage.insert_in_progress_review(
            **kwargs,
            evaluator_id="evaluator_id2",
            input_evaluation_id="input_evaluation_id",
        )
        await reviews_storage.insert_in_progress_review(
            **kwargs,
            evaluator_id="evaluator_id",
            input_evaluation_id="input_evaluation_id2",
        )

    async def test_insert_in_progress_review_with_complete_review(
        self,
        reviews_storage: MongoReviewsStorage,
        reviews_col: AsyncCollection,
    ):
        # Check that we don't update the status of an existing review
        await reviews_col.insert_one(
            dump_model(
                _review_doc(
                    id="66568f3c40d79b0d69ece4a8",
                    reviewer=ReviewDocument.AIReviewer(
                        evaluator_id="evaluator_id",
                        input_evaluation_id="input_evaluation_id",
                    ),
                    status="completed",
                ),
            ),
        )

        with pytest.raises(DuplicateValueError):
            await reviews_storage.insert_in_progress_review(
                task_id="task_id",
                task_schema_id=1,
                task_input_hash="task_input_hash",
                task_output_hash="task_output_hash",
                evaluator_id="evaluator_id",
                input_evaluation_id="input_evaluation_id",
            )

        # retrieve doc and check that the status is still in_progress
        assert await reviews_col.count_documents({}) == 1

        doc = await reviews_col.find_one({"_id": ObjectId("66568f3c40d79b0d69ece4a8")})
        assert doc is not None
        assert doc["status"] == "completed"


class TestCompleteReview:
    async def test_complete_review(self, reviews_storage: MongoReviewsStorage, reviews_col: AsyncCollection):
        await reviews_col.insert_one(
            dump_model(_review_doc(id="66568f3c40d79b0d69ece4a8", reviewer_type="ai", status="in_progress")),
        )

        await reviews_storage.complete_review(
            review_id="66568f3c40d79b0d69ece4a8",
            outcome="positive",
            comment="comment",
            confidence_score=0.5,
            run_identifier=RunIdentifier(tenant="test_tenant", run_id="run_id", task_id="task_id", task_schema_id=1),
        )

        doc = await reviews_col.find_one({"_id": ObjectId("66568f3c40d79b0d69ece4a8")})
        assert doc is not None
        assert doc["status"] == "completed"
        assert doc["outcome"] == "positive"
        assert doc["comment"] == "comment"

        # Fails if called a second time since the review is completed
        with pytest.raises(ObjectNotFoundException):
            await reviews_storage.complete_review(
                review_id="66568f3c40d79b0d69ece4a8",
                outcome="positive",
            )


class TestEvalHashesForReview:
    @pytest.mark.parametrize(
        ("review", "expected"),
        [
            (ReviewSearchOptions.ANY, {"21e617d1accb328b619a7db8b074e2b1", "cf304f30f1e38075a465d0ae2abd432d"}),
            (ReviewSearchOptions.POSITIVE, {"21e617d1accb328b619a7db8b074e2b1"}),
            (ReviewSearchOptions.NEGATIVE, {"cf304f30f1e38075a465d0ae2abd432d"}),
            (ReviewSearchOptions.UNSURE, set[str]()),
        ],
    )
    async def test_eval_hashes_for_review(
        self,
        reviews_col: AsyncCollection,
        reviews_storage: MongoReviewsStorage,
        review: ReviewSearchOptions,
        expected: set[str],
    ):
        # Insert test documents with different outcomes
        await reviews_col.insert_many(
            [
                dump_model(doc)
                for doc in [
                    _review_doc(id="66568f3c40d79b0d69ece4a8", reviewer_type="ai", task_input_hash="i1"),
                    _review_doc(
                        id="66568f3c40d79b0d69ece4a9",
                        reviewer_type="ai",
                        task_input_hash="i2",
                        is_stale=True,
                        outcome="positive",
                    ),
                    _review_doc(
                        id="66568f3c40d79b0d69ece4aa",
                        reviewer_type="ai",
                        task_output_hash="o3",
                        outcome="negative",
                    ),
                ]
            ],
        )

        # Test getting all eval hashes
        eval_hashes = await reviews_storage.eval_hashes_for_review("task_id", review=review)
        assert eval_hashes == expected


class TestReviewsForEvalHashes:
    @pytest.mark.parametrize(
        ("hashes", "expected"),
        (
            (
                {"21e617d1accb328b619a7db8b074e2b1"},
                {"66568f3c40d79b0d69ece4a8"},
            ),
            (
                {"21e617d1accb328b619a7db8b074e2b1", "d9ad253a0274bbd5535b5ca106e9e071"},
                {"66568f3c40d79b0d69ece4a8"},
            ),
        ),
    )
    async def test_reviews_for_eval_hashes(
        self,
        reviews_col: AsyncCollection,
        reviews_storage: MongoReviewsStorage,
        hashes: set[str],
        expected: set[str],
    ):
        # Insert test documents with different eval hashes
        await reviews_col.insert_many(
            [
                dump_model(doc)
                for doc in [
                    #
                    _review_doc(id="66568f3c40d79b0d69ece4a8", reviewer_type="ai", task_input_hash="i1"),
                    _review_doc(id="66568f3c40d79b0d69ece4c8", reviewer_type="user"),
                    # Stale review
                    _review_doc(
                        id="66568f3c40d79b0d69ece4a9",
                        reviewer_type="ai",
                        task_input_hash="i2",
                        is_stale=True,
                    ),
                    # Different task_id
                    _review_doc(
                        id="66568f3c40d79b0d69ece4aa",
                        reviewer_type="ai",
                        task_input_hash="i1",
                        task_id="task_id1",
                    ),
                ]
            ],
        )

        # Test getting reviews for specific eval hashes
        review_ids = {r.id async for r in reviews_storage.reviews_for_eval_hashes("task_id", hashes)}
        assert review_ids == expected


class TestEvalHashesWithUserReviews:
    @pytest.mark.parametrize(
        ("input_hashes", "expected"),
        [
            # Case 1: All hashes have reviews
            ({"hash1"}, {"e1", "e6"}),
            # Case 2: Some hashes don't have reviews
            ({"hash1", "hash2", "hash3"}, {"e1", "e2", "e6"}),
            # Case 3: No hashes have reviews
            ({"hash4", "hash5"}, set[str]()),
            # Case 4: Empty input set
            (set[str](), set[str]()),
        ],
    )
    async def test_eval_hashes_with_user_reviews(
        self,
        reviews_col: AsyncCollection,
        reviews_storage: MongoReviewsStorage,
        input_hashes: set[str],
        expected: set[str],
    ):
        # Insert test documents with different input hashes
        await reviews_col.insert_many(
            [
                dump_model(doc)
                for doc in [
                    # Non-stale reviews
                    _review_doc(task_input_hash="hash1", eval_hash="e1"),
                    _review_doc(task_input_hash="hash1", eval_hash="e6"),
                    _review_doc(task_input_hash="hash2", eval_hash="e2"),
                    # Stale review - should not affect result
                    _review_doc(task_input_hash="hash1", is_stale=True, eval_hash="e4"),
                    # Different task_id - should not affect result
                    _review_doc(task_input_hash="hash3", task_id="different_task", eval_hash="e5"),
                ]
            ],
        )

        result = await reviews_storage.eval_hashes_with_user_reviews("task_id", 1, input_hashes)
        assert result == expected


class TestAIReviewUnique:
    async def test_ai_review_unique(self, reviews_col: AsyncCollection):
        # Check that we cannot insert multiple AI reviews that have the same evaluator_id and input_evaluation_id
        await reviews_col.delete_many({})

        doc = _review_doc(reviewer_type="ai")
        assert doc.reviewer
        assert doc.reviewer.reviewer_type == "ai", "sanity"
        assert doc.is_stale is False, "sanity"
        await reviews_col.insert_one(dump_model(doc))

        def _dump_with_update(doc: ReviewDocument, update: dict[str, Any]):
            dumped = dump_model(doc, exclude={"id"})
            for k, v in update.items():
                set_at_keypath_str(dumped, k, v)
            return dumped

        with pytest.raises(DuplicateKeyError):
            await reviews_col.insert_one(_dump_with_update(doc, {}))

        # Even if the review is stale
        with pytest.raises(DuplicateKeyError):
            await reviews_col.insert_one(_dump_with_update(doc, {"is_stale": True}))

        # But all good if the evaluator id, evaluation_input_id are different
        await reviews_col.insert_one(_dump_with_update(doc, {"reviewer.evaluator_id": "bla"}))

        # But all good if the evaluator id, evaluation_input_id are different
        await reviews_col.insert_one(_dump_with_update(doc, {"reviewer.input_evaluation_id": "bla"}))

        # For a different task_id or tenant, I can insert the same AI review again
        await reviews_col.insert_one(_dump_with_update(doc, {"task_id": "task_id1"}))
        await reviews_col.insert_one(_dump_with_update(doc, {"tenant": "tenant1"}))
