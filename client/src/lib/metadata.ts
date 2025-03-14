import { TenantID } from '@/types/aliases';
import { TaskSchemaParams } from './routeFormatter';

export function generateMetadataWithTitle(
  title: string,
  params: TaskSchemaParams
) {
  return {
    title: `${title} · ${decodeURIComponent(params.tenant)}/${params.taskId}`,
  };
}

export function generateMetadataWithTitleForTenant(
  title: string,
  tenant: TenantID
) {
  return {
    title: `${title} · ${decodeURIComponent(tenant)}`,
  };
}
