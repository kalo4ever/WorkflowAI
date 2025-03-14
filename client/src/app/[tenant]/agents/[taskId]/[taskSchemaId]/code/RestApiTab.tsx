'use client';

import { useMemo } from 'react';
import { CodeBlock } from '@/components/v2/CodeBlock';
import { PROD_RUN_URL } from '@/lib/constants';
import { TaskRun } from '@/types';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { VersionEnvironment, VersionV1 } from '@/types/workflowAI';
import { versionForCodeGeneration } from './utils';

type RestApiTabProps = {
  tenant: TenantID;
  taskId: TaskID;
  taskSchemaId: TaskSchemaID;
  taskRun: TaskRun | undefined;
  environment?: VersionEnvironment;
  version: VersionV1;
  apiUrl: string | undefined;
};

export function RestApiTab(props: RestApiTabProps) {
  const {
    tenant,
    taskId,
    taskSchemaId,
    environment,
    taskRun: rawTaskRun,
    version,
    apiUrl,
  } = props;

  const taskRunJSON = useMemo(
    () => JSON.stringify({ task_output: rawTaskRun?.task_output }, null, 2),
    [rawTaskRun]
  );

  const payload = useMemo(() => {
    if (!rawTaskRun) {
      return undefined;
    }
    const v = versionForCodeGeneration(environment, version);

    if (!!environment) {
      return {
        task_input: rawTaskRun.task_input,
        version: v,
        use_cache: 'auto',
      };
    }

    return {
      task_input: rawTaskRun.task_input,
      version: v,
      use_cache: 'auto',
    };
  }, [rawTaskRun, environment, version]);

  const payloadJSON = useMemo(
    () => JSON.stringify(payload, null, 2),
    [payload]
  );

  const code = useMemo(() => {
    const host = apiUrl ?? PROD_RUN_URL;
    return [
      `POST /v1/${tenant}/tasks/${taskId}/schemas/${taskSchemaId}/run`,
      `Host: ${host}`,
      `Authorization: Bearer {Add your API key here}`,
      'Content-Type: application/json',
      '',
      payloadJSON,
      '',
      '# Cache options:',
      '# - "auto" (default): if a previous successful run is found and the temperature is set to 0, it will be used. Otherwise, the model is called.',
      '# - "always": the cached output is returned when available, regardless of the temperature value',
      '# - "never": the cache is never used',
    ].join('\n');
  }, [apiUrl, tenant, taskId, taskSchemaId, payloadJSON]);

  return (
    <div className='flex flex-col w-full h-full overflow-y-auto'>
      <CodeBlock language='HTTP Request' snippet={code} />
      <CodeBlock
        language='JSON'
        snippet={taskRunJSON}
        showCopyButton={false}
        showTopBorder={true}
      />
    </div>
  );
}
