import { captureException } from '@sentry/nextjs';
import { produce } from 'immer';
import { useCallback, useEffect } from 'react';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { TenantID } from '@/types/aliases';
import { PublicOrganizationData } from '@/types/publicOrganizationData';

interface OrganizationBySlugState {
  organizationsBySlug: Map<string, PublicOrganizationData>;
  isLoadingOrganizationBySlug: Map<string, boolean>;
  isInitializedOrganizationBySlug: Map<string, boolean>;
  fetchOrganizationBySlug: (slug: string) => Promise<void>;
}

export const useOrganizationsBySlugStore = create<OrganizationBySlugState>((set, get) => ({
  organizationsBySlug: new Map(),
  isLoadingOrganizationBySlug: new Map(),
  isInitializedOrganizationBySlug: new Map(),
  fetchOrganizationBySlug: async (slug: string) => {
    if (get().isLoadingOrganizationBySlug.get(slug)) return;
    set(
      produce((state) => {
        state.isLoadingOrganizationBySlug.set(slug, true);
      })
    );
    try {
      // Public API that is not prefixed by the tenant ID
      const response = await client.get<PublicOrganizationData>(`/api/data/organizations/${slug}`);
      set(
        produce((state) => {
          state.organizationsBySlug.set(slug, response);
        })
      );
    } catch (error) {
      captureException(error);
      console.error('Error fetching organization:', error);
    } finally {
      set(
        produce((state) => {
          state.isLoadingOrganizationBySlug.set(slug, false);
          state.isInitializedOrganizationBySlug.set(slug, true);
        })
      );
    }
  },
}));

export function useOrganizationBySlug(slug: TenantID) {
  const isInitialized = useOrganizationsBySlugStore((state) => state.isInitializedOrganizationBySlug.get(slug));
  const isLoading = useOrganizationsBySlugStore((state) => state.isLoadingOrganizationBySlug.get(slug));
  const organization = useOrganizationsBySlugStore((state) => state.organizationsBySlug.get(slug));

  const fetchOrganizationBySlug = useOrganizationsBySlugStore((state) => state.fetchOrganizationBySlug);

  const refetch = useCallback(() => fetchOrganizationBySlug(slug), [fetchOrganizationBySlug, slug]);

  useEffect(() => {
    if (!isInitialized) {
      fetchOrganizationBySlug(slug);
    }
  }, [isInitialized, fetchOrganizationBySlug, slug]);

  return {
    organization,
    isLoading,
    isInitialized,
    refetch,
  };
}
