'use server';

import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import { serverFetch } from '@/lib/api/serverAPIClient';
import { auth } from '@/lib/auth';
import { RunV1 } from '@/types/workflowAI';

async function fetchSchemaId(
  tenant: string | undefined,
  schemaId: number | undefined,
  taskId: string,
  runId: string
) {
  if (schemaId !== undefined) {
    return schemaId;
  }
  const run = await serverFetch(
    `/v1/${tenant ?? '_'}/agents/${taskId}/runs/${runId}`,
    {
      method: 'GET',
    },
    // Cannot set cookie in a page
    false
  );
  const runData: RunV1 = await run.json();
  return runData.task_schema_id;
}

type RunRedirectPageProps = {
  runId: string;
  taskId: string;
  tenant?: string;
  schemaId?: number;
};

export default async function RunRedirect({
  runId,
  taskId,
  tenant,
  schemaId,
}: RunRedirectPageProps) {
  const { orgSlug, redirectToSignIn } = auth();

  if (!orgSlug) {
    const headersList = headers();
    const fullUrl =
      headersList.get('x-url') || headersList.get('referer') || '';

    return redirectToSignIn({
      returnBackUrl: fullUrl,
    });
  }

  const finalSchemaId = await fetchSchemaId(tenant, schemaId, taskId, runId);

  const tenantURL = tenant === '_' ? orgSlug : tenant;
  return redirect(
    `/${tenantURL}/agents/${taskId}/${finalSchemaId}/runs?taskRunId=${runId}`
  );
}
