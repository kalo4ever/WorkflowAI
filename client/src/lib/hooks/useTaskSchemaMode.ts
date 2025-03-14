import { first } from 'lodash';
import { useMemo } from 'react';
import { TaskSchemaResponseWithSchema } from '@/types';
import { extractFormats } from '../schemaFileUtils';

export function useTaskSchemaMode(
  taskSchema: TaskSchemaResponseWithSchema | undefined
) {
  return useMemo(
    () => first(extractFormats(taskSchema?.input_schema.json_schema)),
    [taskSchema]
  );
}
