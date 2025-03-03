import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { OrganizationInformation } from '@/app/api/users/organizations/[organizationId]/route';
import { client } from '@/lib/api';

enableMapSet();

interface ClerkOrganizationState {
  clerkOrganizationsById: Record<string, OrganizationInformation>;
  isLoadingById: Record<string, boolean>;
  isInitializedById: Record<string, boolean>;
  fetchClerkOrganization: (
    organizationId: string
  ) => Promise<OrganizationInformation | undefined>;
  fetchClerkOrganizations: (organizationIds: string[]) => Promise<void>;
}

export const useClerkOrganizationStore = create<ClerkOrganizationState>(
  (set, get) => ({
    clerkOrganizationsById: {},
    isLoadingById: {},
    isInitializedById: {},

    fetchClerkOrganization: async (organizationId: string) => {
      const currentOrg = get().clerkOrganizationsById[organizationId];
      if (currentOrg) {
        return currentOrg;
      }
      if (get().isLoadingById[organizationId]) return;
      set(
        produce((state) => {
          state.isLoadingById[organizationId] = true;
        })
      );
      let organization: OrganizationInformation | undefined;

      try {
        organization = await client.get<OrganizationInformation>(
          `/api/users/organizations/${organizationId}`
        );
        set(
          produce((state) => {
            state.clerkOrganizationsById[organizationId] = organization;
          })
        );
      } catch (error) {
        console.error('Error fetching Clerk organization:', error);
      }

      set(
        produce((state) => {
          state.isLoadingById[organizationId] = false;
          state.isInitializedById[organizationId] = true;
        })
      );
      return organization;
    },
    fetchClerkOrganizations: async (organizationIds: string[]) => {
      await Promise.all(organizationIds.map(get().fetchClerkOrganization));
    },
  })
);
