from .hash import compute_obj_hash


def test_compute_obj_hash() -> None:
    obj = {"actual": {"category": "A"}, "input": {"value": "sugar"}}

    assert compute_obj_hash(obj) == "98b629d6b235b4281585f240a72d7137"

    obj = {"input": {"value": "sugar"}, "actual": {"category": "A"}}

    assert compute_obj_hash(obj) == "98b629d6b235b4281585f240a72d7137"
