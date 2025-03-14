import { isEqual } from 'lodash';
import { useMemo } from 'react';
import { replaceFileData } from '@/lib/schemaFileUtils';
import {
  JsonSchema,
  JsonValueSchema,
  TaskRun,
  TaskSchemaResponseWithSchema,
} from '@/types';
import { VersionV1 } from '@/types/workflowAI';

const DATA_PLACEHOLDER = '<base 64 encoded data>';

export const MP3_SAMPLE_URL =
  'https://workflowai.blob.core.windows.net/workflowai-public/sample.mp3';
export const JPG_SAMPLE_URL =
  'https://workflowai.blob.core.windows.net/workflowai-public/sample.jpeg';

function stripLargeData(obj: Record<string, unknown>): Record<string, unknown> {
  const sanitizedData =
    'data' in obj && typeof obj.data === 'string' && obj.data.length > 300000
      ? DATA_PLACEHOLDER
      : obj.data;

  return { data: sanitizedData, content_type: obj.content_type };
}

function fileDataToURLReplacer(
  obj: Record<string, unknown>,
  schema: JsonValueSchema
): Record<string, unknown> {
  if ('url' in obj) {
    return { url: obj.url };
  }
  if (schema.format === 'audio') {
    return {
      url: MP3_SAMPLE_URL,
    };
  }

  if (
    'properties' in schema &&
    schema.properties &&
    'url' in schema.properties
  ) {
    return {
      url: JPG_SAMPLE_URL,
    };
  }

  return stripLargeData(obj);
}

function fileDataToDataReplacer(
  obj: Record<string, unknown>,
  schema: JsonValueSchema
): Record<string, unknown> {
  if (!obj.data) {
    return {
      content_type: schema.format === 'audio' ? 'audio/mpeg' : 'image/jpeg',
      data: DATA_PLACEHOLDER,
    };
  }
  return stripLargeData(obj);
}

export function generateInputsForCodeGeneration(
  taskRuns: TaskRun[] | undefined,
  inputSchema: JsonSchema | undefined
): [TaskRun | undefined, Record<string, unknown> | undefined] {
  const run = taskRuns?.[0];
  if (!run) {
    return [undefined, undefined];
  }
  if (!inputSchema) {
    return [run, undefined];
  }
  const taskInput = replaceFileData(
    inputSchema,
    run.task_input,
    fileDataToURLReplacer
  );
  if (isEqual(run.task_input, taskInput)) {
    return [run, undefined];
  }
  // Otherwise we generate a secondary input
  const secondaryInput = replaceFileData(
    inputSchema,
    run.task_input,
    fileDataToDataReplacer
  );
  // For very large data there is a case where
  // both inputs are the same so we add a safety here

  return [
    { ...run, task_input: taskInput },
    isEqual(taskInput, secondaryInput) ? undefined : secondaryInput,
  ];
}

export function useTaskRunWithSecondaryInput(
  taskRuns: TaskRun[] | undefined,
  taskSchema: Pick<TaskSchemaResponseWithSchema, 'input_schema'> | undefined
) {
  return useMemo(
    () =>
      generateInputsForCodeGeneration(
        taskRuns,
        taskSchema?.input_schema.json_schema
      ),
    [taskRuns, taskSchema]
  );
}

export function versionForCodeGeneration(
  environment: string | undefined,
  version: VersionV1 | undefined
) {
  if (environment) {
    return environment;
  }
  if (version?.semver) {
    return `${version.semver[0]}.${version.semver[1]}`;
  }
  return version?.iteration ?? 1;
}
