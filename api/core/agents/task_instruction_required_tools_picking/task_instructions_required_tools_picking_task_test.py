from core.agents.task_instruction_required_tools_picking.task_instructions_required_tools_picking_task import (
    TaskInstructionsRequiredToolsPickingTaskOutput,
)


def test_output_has_default_factory():
    # Good enough to instantiate without any required tools
    assert TaskInstructionsRequiredToolsPickingTaskOutput()
    assert TaskInstructionsRequiredToolsPickingTaskOutput.model_validate({})
