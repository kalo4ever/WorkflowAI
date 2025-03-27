import { generateMetadataWithTitleForTenant } from '@/lib/metadata';
import { TenantID } from '@/types/aliases';
import { TasksContainer } from './agents/tasks/TasksContainer';

export async function generateMetadata({ params }: { params: { tenant: TenantID } }) {
  return generateMetadataWithTitleForTenant('AI Agents', params.tenant);
}

export default function TasksPage({ params: { tenant } }: { params: { tenant: TenantID } }) {
  return <TasksContainer tenant={tenant} />;
}
