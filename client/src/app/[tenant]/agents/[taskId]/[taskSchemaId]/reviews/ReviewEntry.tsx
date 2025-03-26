import { useCallback } from 'react';
import { ObjectViewer } from '@/components/ObjectViewer/ObjectViewer';
import { useTaskEvaluation } from '@/store/task_evaluation';
import { TenantID } from '@/types/aliases';
import { TaskID } from '@/types/aliases';
import { TaskSchemaID } from '@/types/aliases';
import { SerializableTaskIOWithSchema } from '@/types/task';
import { InputEvaluationData } from '@/types/workflowAI';
import { ReviewEntryInstructions } from './ReviewEntryInstructions';
import { ReviewInputOutputEntry } from './ReviewInputOutputEntry';

type ReviewEntryProps = {
  tenant: TenantID | undefined;
  taskId: TaskID;
  taskSchemaId: TaskSchemaID;
  data: InputEvaluationData;
  schemaInput: SerializableTaskIOWithSchema | undefined;
  schemaOutput: SerializableTaskIOWithSchema | undefined;
  isInDemoMode: boolean;
};

export function ReviewEntry(props: ReviewEntryProps) {
  const { data, schemaInput, schemaOutput, tenant, taskId, taskSchemaId, isInDemoMode } = props;

  const updateEvaluationInputs = useTaskEvaluation((state) => state.updateEvaluationInputs);

  const handleUpdateEvaluationInputs = useCallback(
    (value: Record<string, unknown>, isCorrect: boolean) => {
      if (isCorrect) {
        return updateEvaluationInputs(tenant, taskId, taskSchemaId, data.task_input_hash, {
          add_correct_output: value,
        });
      } else {
        return updateEvaluationInputs(tenant, taskId, taskSchemaId, data.task_input_hash, {
          add_incorrect_output: value,
        });
      }
    },
    [tenant, taskId, taskSchemaId, data.task_input_hash, updateEvaluationInputs]
  );

  const updateInstructions = useCallback(
    (instructions: string) => {
      return updateEvaluationInputs(tenant, taskId, taskSchemaId, data.task_input_hash, {
        update_input_evaluation_instructions: instructions,
      });
    },
    [tenant, taskId, taskSchemaId, data.task_input_hash, updateEvaluationInputs]
  );

  return (
    <div className='pr-2 py-2.5 flex items-stretch gap-4 rounded-[2px] w-full border-b border-gray-100 last:border-transparent'>
      <div className='flex flex-col w-[25%] -ml-2 mr-2'>
        <div className='relative h-full min-h-[200px]'>
          <ObjectViewer
            value={data.task_input}
            schema={schemaInput?.json_schema}
            defs={schemaInput?.json_schema?.$defs}
            className='w-full absolute inset-0 overflow-y-auto'
          />
        </div>
      </div>
      <div className='flex flex-col gap-3 items-start w-[25%]'>
        {data.correct_outputs.map((output, index) => (
          <ReviewInputOutputEntry
            key={index}
            value={output}
            schema={schemaOutput}
            index={index}
            isCorrect={true}
            onCorrectChange={handleUpdateEvaluationInputs}
            isInDemoMode={isInDemoMode}
          />
        ))}
      </div>
      <div className='flex flex-col gap-3 items-start h-max w-[25%]'>
        {data.incorrect_outputs.map((output, index) => (
          <ReviewInputOutputEntry
            key={index}
            value={output}
            schema={schemaOutput}
            index={index}
            isCorrect={false}
            onCorrectChange={handleUpdateEvaluationInputs}
            isInDemoMode={isInDemoMode}
          />
        ))}
      </div>
      <div className='flex flex-col items-start w-[25%] h-full'>
        <ReviewEntryInstructions
          instructions={data.evaluation_instructions}
          onChange={updateInstructions}
          disabled={isInDemoMode}
        />
      </div>
    </div>
  );
}
