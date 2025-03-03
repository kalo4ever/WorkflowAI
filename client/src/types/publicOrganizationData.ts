import { Provider } from '@/types/workflowAI';

export type PublicOrganizationData = {
  tenant?: string;
  slug?: string;
  name?: string | null;
  org_id?: string | null;
  provider: Provider;
};
