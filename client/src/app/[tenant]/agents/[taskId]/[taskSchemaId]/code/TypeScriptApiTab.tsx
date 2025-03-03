'use client';

import cloneDeep from 'lodash/cloneDeep';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useLocalStorage } from 'usehooks-ts';
import { getPlaygroundSnippets } from '@/code-generator';
import { Switch } from '@/components/ui/Switch';
import { CodeBlock } from '@/components/v2/CodeBlock';
import { TaskRun } from '@/types';
import { TaskSchemaResponseWithSchema } from '@/types/task';
import { VersionEnvironment, VersionV1 } from '@/types/workflowAI';
import { versionForCodeGeneration } from './utils';

type TypeScriptApiTabProps = {
  taskSchema: TaskSchemaResponseWithSchema | undefined;
  taskRun: TaskRun | undefined;
  version: VersionV1 | undefined;
  environment: VersionEnvironment | undefined;
  apiUrl: string | undefined;
  secondaryInput: Record<string, unknown> | undefined;
};

export function TypeScriptApiTab(props: TypeScriptApiTabProps) {
  const { taskSchema, taskRun, version, environment, apiUrl, secondaryInput } =
    props;

  const [streamRunsForGroupId, setStreamRunsForGroupId] = useLocalStorage<
    Record<number, boolean>
  >('streamRunsForGroupId', {});

  const streamRuns = useMemo(() => {
    const id = version?.iteration;
    if (!id) {
      return false;
    }
    return streamRunsForGroupId[id] ?? false;
  }, [streamRunsForGroupId, version]);

  const setStreamRuns = useCallback(
    (value: boolean) => {
      const id = version?.iteration;
      if (!id) {
        return;
      }
      setStreamRunsForGroupId({
        ...streamRunsForGroupId,
        [id]: value,
      });
    },
    [streamRunsForGroupId, setStreamRunsForGroupId, version]
  );

  const [snippets, setSnippets] =
    useState<Awaited<ReturnType<typeof getPlaygroundSnippets>>>();

  useEffect(() => {
    // The only required data is the task schema
    if (taskSchema) {
      getPlaygroundSnippets({
        taskId: taskSchema.task_id,
        taskName: taskSchema.name,
        schema: {
          id: taskSchema.schema_id,
          input: cloneDeep(taskSchema.input_schema.json_schema),
          output: cloneDeep(taskSchema.output_schema.json_schema),
        },
        version: JSON.stringify(versionForCodeGeneration(environment, version)),
        example: {
          input: taskRun?.task_input || {
            replaceWith: 'your input data',
          },
          output: taskRun?.task_output || {
            replaceWith: 'your output data',
          },
        },
        api: {
          // Only display API URL in doc if it's not production
          // since the lib defaults to production endpoint if not passed
          url: apiUrl ?? null,
        },
        secondaryInput,
      }).then(setSnippets);
    }
  }, [taskSchema, version, environment, taskRun, apiUrl, secondaryInput]);

  const snippetContent = useMemo(() => {
    if (!snippets) {
      return '';
    }

    return streamRuns
      ? [
          '// Initialize WorkflowAI Client',
          snippets.initializeClient.code,
          '',
          '// Initialize Your AI agent',
          snippets.initializeTask.code,
          '',
          '// Run Your AI agent',
          snippets.streamRunTask.code,
        ].join('\n')
      : [
          '// Initialize WorkflowAI Client',
          snippets.initializeClient.code,
          '',
          '// Initialize Your AI agent',
          snippets.initializeTask.code,
          '',
          '// Run Your AI agent',
          snippets.runTask.code,
        ].join('\n');
  }, [snippets, streamRuns]);

  if (!snippets) {
    return (
      <div className='flex-1 flex items-center justify-center'>
        Failed to load AI agent snippet
      </div>
    );
  }

  return (
    <div className='flex flex-col w-full h-full overflow-y-auto'>
      <div className='flex flex-col gap-2 py-4 px-4 text-sm'>
        <div className='flex items-center gap-3'>
          <Switch
            checked={streamRuns}
            onCheckedChange={setStreamRuns}
            className='data-[state=checked]:bg-indigo-700'
          />
          Stream partial results
        </div>
      </div>

      <CodeBlock
        language={snippets.installSdk.language}
        snippet={snippets.installSdk.code}
        showTopBorder={true}
      />
      <CodeBlock
        title={'TypeScript'}
        language={snippets.initializeClient.language}
        snippet={snippetContent.toString()}
        showTopBorder={true}
      />
    </div>
  );
}
