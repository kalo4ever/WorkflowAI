'use server';

import RunRedirect from '@/components/server/RunRedirect';

export default async function RunRedirectPage({
  params,
  searchParams,
}: {
  params: { taskId: string; runId: string; tenant?: string };
  searchParams?: { schemaId?: number };
}) {
  return (
    <RunRedirect runId={params.runId} taskId={params.taskId} tenant={params.tenant} schemaId={searchParams?.schemaId} />
  );
}
