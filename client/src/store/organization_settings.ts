import { produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { JsonSchema } from '@/types';
import {
  OrganizationSettings,
  Provider,
  ProviderSettings,
} from '../types/workflowAI/models';
import { rootTenantPath } from './utils';

export type ProviderConfig = {
  provider: Provider;
};

interface OrganizationSettingsState {
  settings: OrganizationSettings | undefined;
  isLoading: boolean;
  isInitialized: boolean;
  fetchOrganizationSettings: () => Promise<void>;
  addProviderConfig: (config: ProviderConfig) => Promise<void>;
  deleteProviderConfig: (configID: string) => Promise<void>;
  isLoadingProviderSchemas: boolean;
  providerSchemas: Record<Provider, JsonSchema> | undefined;
  fetchProviderSchemas: () => Promise<void>;
}

export const useOrganizationSettings = create<OrganizationSettingsState>(
  (set) => ({
    settings: undefined,
    isLoading: false,
    isInitialized: false,
    fetchOrganizationSettings: async () => {
      set(
        produce((state: OrganizationSettingsState) => {
          state.isLoading = true;
        })
      );
      try {
        const settings = await client.get<OrganizationSettings>(
          `${rootTenantPath()}/organization/settings`
        );

        set(
          produce((state: OrganizationSettingsState) => {
            state.settings = settings;
          })
        );
      } finally {
        set(
          produce((state: OrganizationSettingsState) => {
            state.isLoading = false;
            state.isInitialized = true;
          })
        );
      }
    },
    addProviderConfig: async (config: ProviderConfig) => {
      const providerSettings = await client.post<
        ProviderConfig,
        ProviderSettings
      >(`${rootTenantPath()}/organization/settings/providers`, config);
      set(
        produce((state: OrganizationSettingsState) => {
          if (state.settings === undefined) {
            state.settings = { providers: [] };
          }
          state.settings.providers?.push(providerSettings);
          return state;
        })
      );
    },
    deleteProviderConfig: async (configID: string) => {
      await client.del(
        `${rootTenantPath()}/organization/settings/providers/${configID}`
      );
      set(
        produce((state: OrganizationSettingsState) => {
          if (state.settings === undefined) {
            return state;
          }
          state.settings.providers = state.settings.providers?.filter(
            (provider) => provider.id !== configID
          );
          return state;
        })
      );
    },
    providerSchemas: undefined,
    isLoadingProviderSchemas: false,
    fetchProviderSchemas: async () => {
      set({ isLoadingProviderSchemas: true });
      try {
        const providerSchemas = await client.get<Record<Provider, JsonSchema>>(
          `${rootTenantPath()}/organization/settings/providers/schemas`
        );
        set({ providerSchemas });
      } finally {
        set({ isLoadingProviderSchemas: false });
      }
    },
  })
);
