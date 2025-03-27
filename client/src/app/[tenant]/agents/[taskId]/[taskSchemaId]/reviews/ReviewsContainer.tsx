'use client';

import { useCallback } from 'react';
import { Loader } from '@/components/ui/Loader';
import { PageContainer } from '@/components/v2/PageContainer';
import { useDemoMode } from '@/lib/hooks/useDemoMode';
import { useTaskSchemaParams } from '@/lib/hooks/useTaskParams';
import { useOrFetchTask } from '@/store';
import { useOrFetchCurrentTaskSchema, useOrFetchEvaluation, useOrFetchEvaluationInputs } from '@/store/fetchers';
import { useTaskEvaluation } from '@/store/task_evaluation';
import { ReviewEntry } from './ReviewEntry';
import { ReviewMainInstructions } from './ReviewMainInstructions';
import { ReviewsHeader } from './ReviewsHeader';

export default function ReviewsContainer() {
  const { tenant, taskId, taskSchemaId } = useTaskSchemaParams();

  const { task, isInitialized: isTaskInitialized } = useOrFetchTask(tenant, taskId);

  const { taskSchema: currentTaskSchema, isInitialized: isTaskSchemaInitialized } = useOrFetchCurrentTaskSchema(
    tenant,
    taskId,
    taskSchemaId
  );

  const { evaluation, isInitialized: isEvaluationInitialized } = useOrFetchEvaluation(tenant, taskId, taskSchemaId);

  const { evaluationInputs, isInitialized: isEvaluationInputsInitialized } = useOrFetchEvaluationInputs(
    tenant,
    taskId,
    taskSchemaId
  );

  const sortedEvaluationInputs = evaluationInputs?.sort((a, b) => {
    return a.task_input_hash.localeCompare(b.task_input_hash);
  });

  const updateEvaluation = useTaskEvaluation((state) => state.updateEvaluation);

  const handleUpdateEvaluation = useCallback(
    (instructions: string) => {
      updateEvaluation(tenant, taskId, taskSchemaId, instructions);
    },
    [tenant, taskId, taskSchemaId, updateEvaluation]
  );

  const { isInDemoMode } = useDemoMode();

  if (!task || !isTaskSchemaInitialized || !isEvaluationInitialized || !isEvaluationInputsInitialized) {
    return <Loader centered />;
  }

  return (
    <PageContainer task={task} isInitialized={isTaskInitialized} name='Reviews' showCopyLink={true}>
      <div className='flex flex-col h-full w-full overflow-hidden font-lato px-4 py-4 gap-4'>
        <ReviewMainInstructions
          instructions={evaluation?.evaluation_instructions}
          onChange={handleUpdateEvaluation}
          disabled={isInDemoMode}
        />
        <div className='flex flex-col w-full flex-1 border border-gray-200 rounded-[2px] px-2 pb-2 bg-gradient-to-b from-white/50 to-white/20 overflow-hidden'>
          <ReviewsHeader />
          <div className='flex flex-col w-full flex-1 overflow-y-auto'>
            {sortedEvaluationInputs?.map((data) => (
              <ReviewEntry
                key={data.task_input_hash}
                tenant={tenant}
                taskId={taskId}
                taskSchemaId={taskSchemaId}
                data={data}
                schemaInput={currentTaskSchema?.input_schema}
                schemaOutput={currentTaskSchema?.output_schema}
                isInDemoMode={isInDemoMode}
              />
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
