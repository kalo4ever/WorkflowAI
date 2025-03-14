import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';

enableMapSet();

export type TokenScope = { userID?: string; orgID?: string };

export function tokenScopeKey(scope: TokenScope) {
  return `${scope.userID ?? ''}${scope.orgID ?? ''}`;
}

// No need to consider initialized here
// We should just always try and fetch a token
interface TokenState {
  tokenByScope: Map<string, string | undefined>;
  isLoadingByScope: Map<string, boolean>;
  fetchToken(scope: TokenScope): Promise<void>;
}

function tokenScopeQueryParams(scope: TokenScope) {
  const params = new URLSearchParams();
  if (scope.userID) params.set('userID', scope.userID);
  if (scope.orgID) params.set('orgID', scope.orgID);
  return params;
}

// Scoping the token by user and org
// Ultimately, we should just use the clerk token directly
// and remove this entire store
export const useToken = create<TokenState>((set, get) => ({
  tokenByScope: new Map(),
  isLoadingByScope: new Map(),
  fetchToken: async (scope) => {
    const scopeKey = tokenScopeKey(scope);
    if (get().isLoadingByScope.get(scopeKey)) return;
    set(
      produce((state) => {
        state.isLoadingByScope.set(scopeKey, true);
      })
    );
    const queryParams = tokenScopeQueryParams(scope);
    try {
      const response = await client.get<{ token: string }>(
        '/api/jwt',
        queryParams
      );
      set(
        produce((state) => {
          state.tokenByScope.set(scopeKey, response.token);
          state.isLoadingByScope.set(scopeKey, false);
        })
      );
    } catch (error) {
      console.error('Failed to fetch token', error);
      set(
        produce((state) => {
          state.isLoadingByScope.set(scopeKey, false);
        })
      );
    }
  },
}));
