'use client';

import { createContext, useContext } from 'react';
import { TenantID } from '@/types/aliases';
import { User } from '@/types/user';

interface AuthContext {
  readonly isLoaded: boolean;
  readonly isSignedIn: boolean;
  readonly tenantSlug: TenantID | undefined;
  readonly tenantId: string | undefined;
  readonly user: Readonly<User> | undefined;
  readonly hasOrganization: boolean;
}

export const AuthContext = createContext<AuthContext>({
  isLoaded: false,
  isSignedIn: false,
  tenantSlug: undefined,
  user: undefined,
  tenantId: undefined,
  hasOrganization: false,
});

export function useAuth() {
  return useContext(AuthContext);
}

interface AuthUIContext {
  openUserProfile?: () => void;
  openOrganizationProfile?: () => void;
  signOut?: () => void;
}

export const AuthUIContext = createContext<AuthUIContext>({});

export function useAuthUI() {
  return useContext(AuthUIContext);
}
