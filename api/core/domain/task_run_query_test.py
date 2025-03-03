# class TestAssignValueFromField:
#     _ASSIGN_VALUE_FROM_FIELD: list[tuple[str, Any, Callable[[SerializableTaskRunQuery], Any], Any]] = [
#         ("task.schema_id", 1, lambda x: x.task_schema_id, 1),
#         ("group.iteration", 1, lambda x: x.group_iteration, 1),
#         ("status", "success", lambda x: x.status, {"success"}),
#     ]

#     @pytest.mark.parametrize(
#         "field_name, value, attr, exp_value",
#         _ASSIGN_VALUE_FROM_FIELD,
#     )
#     def test_assign_value_from_field(
#         self,
#         field_name: str,
#         value: bool,
#         attr: Callable[[SerializableTaskRunQuery], bool],
#         exp_value: Any,
#     ):
#         query, remaining = SerializableTaskRunQuery.from_search_fields(
#             task_id="task_id",
#             search_fields=[FieldQuery(field_name=field_name, operator=SearchOperator.IS, values=[value])],
#         )
#         assert attr(query) == exp_value
#         assert not remaining
