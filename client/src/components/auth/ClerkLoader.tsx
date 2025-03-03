'use client';

// eslint-disable-next-line no-restricted-imports
import { useClerk, useOrganization, useUser } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { ReactNode, useCallback } from 'react';
import { Loader } from '@/components/ui/Loader';
import { AuthContext, AuthUIContext } from '@/lib/AuthContext';
import { getTenantSlug } from '@/lib/auth_utils';
import { HARDCODED_TENANT } from '@/lib/constants';
import { PATHS } from '@/lib/routeFormatter';
import { TenantID } from '@/types/aliases';
import { clerkUserToUser } from '@/types/user';

export function ClerkLoader({ children }: { children: ReactNode }) {
  const { organization, isLoaded: isOrganizationLoaded } = useOrganization();
  const { isSignedIn, isLoaded: isUserLoaded, user: ckUser } = useUser();
  const { openUserProfile, openOrganizationProfile, signOut } = useClerk();
  const { push } = useRouter();

  // We have to wrap the calls, the openUserProfile and openOrganizationProfile
  // from clerk take arguments so using them as is in components onClick passes
  // an event instead of whatever the function is expecting
  const editUser = useCallback(() => {
    openUserProfile();
  }, [openUserProfile]);

  const editOrganization = useCallback(() => {
    if (organization) {
      openOrganizationProfile();
      return;
    }
    push(PATHS.ORG_SELECTION);
  }, [openOrganizationProfile, organization, push]);

  const wrappedSignOut = useCallback(() => {
    signOut();
  }, [signOut]);

  // TODO: is that actually needed ?
  if (!isUserLoaded) {
    return <Loader centered />;
  }

  const user = ckUser ? clerkUserToUser(ckUser) : undefined;

  return (
    <AuthUIContext.Provider
      value={{
        openUserProfile: editUser,
        openOrganizationProfile: editOrganization,
        signOut: wrappedSignOut,
      }}
    >
      <AuthContext.Provider
        value={{
          isLoaded: isOrganizationLoaded && isUserLoaded,
          isSignedIn: isSignedIn ?? false,
          tenantSlug: getTenantSlug(organization, user) as TenantID,
          tenantId: organization?.id ?? HARDCODED_TENANT,
          user,
          hasOrganization: !!organization,
        }}
      >
        {children}
      </AuthContext.Provider>
    </AuthUIContext.Provider>
  );
}
