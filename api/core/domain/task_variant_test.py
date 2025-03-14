from core.domain.task_io import SerializableTaskIO

from .task_variant import SerializableTaskVariant


class TestComputeHashes:
    def test_simple(self):
        task = SerializableTaskVariant(
            id="",
            task_schema_id=1,
            name="",
            input_schema=SerializableTaskIO.from_json_schema(
                {"type": "object", "properties": {"a": {"type": "string"}}},
            ),
            output_schema=SerializableTaskIO.from_json_schema(
                {"type": "object", "properties": {"b": {"type": "string"}}},
            ),
        )

        input_hash = task.compute_input_hash({"a": "a"})
        assert input_hash == "582af9ef5cdc53d6628f45cb842f874a"
        output_hash = task.compute_output_hash({"b": "b"})
        assert output_hash == "53dd738814f8440b36a9ac19e49e9b8d"

        # Check with extra keys
        input_hash1 = task.compute_input_hash({"a": "a", "b": "b"})
        output_hash1 = task.compute_output_hash({"b": "b", "a": "a"})
        assert input_hash1 == input_hash
        assert output_hash1 == output_hash
