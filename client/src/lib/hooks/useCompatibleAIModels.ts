import { first } from 'lodash';
import { useMemo } from 'react';
import { extractFormats } from '@/lib/schemaFileUtils';
import { useOrFetchAllAiModels } from '@/store';
import { TaskSchemaResponseWithSchema } from '@/types';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { ModelResponse } from '@/types/workflowAI';

export function useTaskSchemaMode(
  taskSchema: TaskSchemaResponseWithSchema | undefined
) {
  return useMemo(
    () => first(extractFormats(taskSchema?.input_schema.json_schema)),
    [taskSchema]
  );
}

type TModeAiModelsProps = {
  tenant: TenantID | undefined;
  taskId: TaskID;
  taskSchemaId: TaskSchemaID;
};

export function filterSupportedModels(models: ModelResponse[]) {
  return models.filter((model) => !model.is_not_supported_reason);
}

export function useCompatibleAIModels(props: TModeAiModelsProps) {
  const { tenant, taskId, taskSchemaId } = props;
  const { models, isInitialized, isLoading } = useOrFetchAllAiModels({
    tenant,
    taskId,
    taskSchemaId,
  });

  const compatibleModels = useMemo(
    () => filterSupportedModels(models),
    [models]
  );

  return {
    compatibleModels,
    isLoading,
    isInitialized,
    allModels: models,
  };
}
