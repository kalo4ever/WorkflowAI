'use client';

import { ReactNode } from 'react';
import { AuthContext } from '@/lib/AuthContext';
import { HARDCODED_TENANT } from '@/lib/constants';
import { TenantID } from '@/types/aliases';

export function NoAuthProvider({ children }: { children: ReactNode }) {
  return (
    <AuthContext.Provider
      value={{
        isLoaded: true,
        isSignedIn: true,
        tenantSlug: HARDCODED_TENANT as TenantID,
        tenantId: HARDCODED_TENANT,
        user: {
          id: '1',
        },
        orgState: 'available',
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
