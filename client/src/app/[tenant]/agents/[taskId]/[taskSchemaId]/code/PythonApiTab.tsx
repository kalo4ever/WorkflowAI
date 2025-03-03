'use client';

import { useMemo, useState } from 'react';
import { Loader } from '@/components/ui/Loader';
import { Switch } from '@/components/ui/Switch';
import { CodeBlock } from '@/components/v2/CodeBlock';
import { useOrFetchTaskSnippet } from '@/store';
import { TaskRun } from '@/types';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { CodeLanguage, InstallInstruction } from '@/types/snippets';
import { VersionEnvironment } from '@/types/workflowAI';

type PythonApiTabProps = {
  tenant: TenantID;
  taskId: TaskID;
  taskSchemaId: TaskSchemaID;
  iteration?: number;
  // TODO: take a versionv1 here like the typescript api tab
  semver?: unknown[] | null;
  environment?: VersionEnvironment;
  taskRun?: TaskRun;
  apiUrl: string | undefined;
  secondaryInput: Record<string, unknown> | undefined;
};

export function PythonApiTab(props: PythonApiTabProps) {
  const {
    tenant,
    taskId,
    taskSchemaId,
    iteration,
    environment,
    taskRun,
    apiUrl,
    secondaryInput,
    semver,
  } = props;

  const [streamRuns, setStreamRuns] = useState(false);

  const { taskSnippet, isInitialized: isSnippetInitialized } =
    useOrFetchTaskSnippet(
      tenant,
      taskId,
      taskSchemaId,
      CodeLanguage.PYTHON,
      taskRun?.task_input,
      iteration,
      environment ?? (semver ? `${semver[0]}.${semver[1]}` : undefined),
      apiUrl,
      secondaryInput
    );

  const finalSnippet = useMemo(() => {
    if (!taskSnippet) {
      return undefined;
    }

    if (
      'stream' in taskSnippet.run &&
      'run' in taskSnippet.run &&
      'common' in taskSnippet.run
    ) {
      const partial = streamRuns ? taskSnippet.run.stream : taskSnippet.run.run;
      return `${partial.imports}\n\n${taskSnippet.run.common}\n\n${partial.code}`;
    }

    return `${taskSnippet.run.code}`;
  }, [taskSnippet, streamRuns]);

  if (!isSnippetInitialized) {
    return <Loader centered />;
  }

  if (!finalSnippet || !taskSnippet) {
    return (
      <div className='flex-1 flex items-center justify-center'>
        Failed to load task snippet
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
        language={taskSnippet[InstallInstruction.SDK].language}
        snippet={taskSnippet[InstallInstruction.SDK].code}
      />
      <CodeBlock
        language={taskSnippet[InstallInstruction.RUN].language}
        snippet={finalSnippet.replace(
          '__WORKFLOWAI_API_TOKEN__',
          'Add your API key here'
        )}
        showTopBorder={true}
      />
    </div>
  );
}
