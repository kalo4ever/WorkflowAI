import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { TenantID } from '@/types/aliases';
import {
  APIKeyResponse,
  APIKeyResponseCreated,
  CreateAPIKeyRequest,
} from '@/types/workflowAI';
import { rootTenantPath } from './utils';

enableMapSet();

interface ApiKeysState {
  apiKeys: APIKeyResponse[];
  isInitialized: boolean;
  isLoading: boolean;
  fetchApiKeys(tenant: TenantID): Promise<void>;
  createApiKey(
    tenant: TenantID | undefined,
    name: string
  ): Promise<APIKeyResponseCreated | undefined>;
  deleteApiKey(tenant: TenantID, apiKeyId: string): Promise<void>;
}

export const useApiKeys = create<ApiKeysState>((set, get) => ({
  apiKeys: [],
  isInitialized: false,
  isLoading: false,
  fetchApiKeys: async (tenant: TenantID | undefined) => {
    if (get().isLoading) {
      return;
    }
    set(
      produce((state: ApiKeysState) => {
        state.isLoading = true;
      })
    );
    try {
      const apiKeys = await client.get<APIKeyResponse[]>(
        `${rootTenantPath(tenant)}/api/keys`
      );
      set(
        produce((state: ApiKeysState) => {
          state.apiKeys = apiKeys;
        })
      );
    } catch (error) {
      console.error('Failed to fetch api keys', error);
    }
    set(
      produce((state: ApiKeysState) => {
        state.isInitialized = true;
        state.isLoading = false;
      })
    );
  },
  createApiKey: async (tenant: TenantID | undefined, name: string) => {
    if (!tenant) {
      return;
    }
    let result: APIKeyResponseCreated | undefined = undefined;
    try {
      const apiKey = await client.post<
        CreateAPIKeyRequest,
        APIKeyResponseCreated
      >(`${rootTenantPath(tenant)}/api/keys`, {
        name,
      });
      set(
        produce((state: ApiKeysState) => {
          state.apiKeys.push(apiKey);
        })
      );
      result = apiKey;
    } catch (error) {
      console.error('Failed to create api key', error);
    }
    return result;
  },
  deleteApiKey: async (tenant: TenantID, apiKeyId: string) => {
    await client.del(`${rootTenantPath(tenant)}/api/keys/${apiKeyId}`);
    set(
      produce((state: ApiKeysState) => {
        state.apiKeys = state.apiKeys.filter((key) => key.id !== apiKeyId);
      })
    );
  },
}));
