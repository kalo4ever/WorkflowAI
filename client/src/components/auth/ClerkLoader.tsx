'use client';

// eslint-disable-next-line no-restricted-imports
import { useClerk, useOrganization, useOrganizationList, useUser } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { ReactNode, useCallback, useEffect, useMemo } from 'react';
import { Loader } from '@/components/ui/Loader';
import { AuthContext, AuthUIContext } from '@/lib/AuthContext';
import { getTenantSlug } from '@/lib/auth_utils';
import { HARDCODED_TENANT } from '@/lib/constants';
import { useTenantID } from '@/lib/hooks/useTaskParams';
import { PATHS } from '@/lib/routeFormatter';
import { TenantID } from '@/types/aliases';
import { clerkUserToUser } from '@/types/user';

export function ClerkLoader({ children }: { children: ReactNode }) {
  const { organization, isLoaded: isOrganizationLoaded } = useOrganization();
  const {
    isLoaded: isOrganizationListLoaded,
    userMemberships,
    userInvitations,
    userSuggestions,
    setActive,
  } = useOrganizationList({
    userMemberships: true,
    userInvitations: true,
    userSuggestions: true,
  });

  const { isSignedIn, isLoaded: isUserLoaded, user: ckUser } = useUser();
  const { openUserProfile, openOrganizationProfile, signOut } = useClerk();
  const { push } = useRouter();

  const orgState = useMemo(() => {
    if (organization) return 'selected';

    if (!isOrganizationListLoaded) return undefined;

    if (!userInvitations.data?.length && !userSuggestions.data?.length && !userMemberships.data?.length)
      return 'unavailable';

    return 'available';
  }, [isOrganizationListLoaded, organization, userInvitations.data, userSuggestions.data, userMemberships.data]);

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
    if (orgState === 'unavailable') {
      push(PATHS.ORG_CREATE);
      return;
    }

    push(PATHS.ORG_SELECTION);
  }, [openOrganizationProfile, organization, push, orgState]);

  const wrappedSignOut = useCallback(() => {
    signOut();
  }, [signOut]);

  const tenant = useTenantID();

  // We split the needed auth correction from the actual action to return a loader instead of the children
  const authCorrection = useMemo(() => {
    if (!tenant || !setActive) {
      return;
    }

    // User has no organization or no invitation so nothing to do
    // Active organization will only be the personal organization
    if (orgState === 'unavailable') {
      return;
    }
    // User is already on the correct organization
    if (tenant === organization?.slug) {
      return;
    }
    // User has access to the organization so we can mark it as active
    if (userMemberships.data?.some((m) => m.organization.slug === tenant)) {
      return 'set-active';
    }
    if (
      userInvitations.data?.some((i) => i.publicOrganizationData.slug === tenant) ||
      userSuggestions.data?.some((s) => s.publicOrganizationData.slug === tenant)
    ) {
      // User has an invitation to the organization so we can redirect to the
      // organization selection page
      // TODO[redirect]: we should redirect to the current page
      return 'select-org';
    }
    return;
  }, [
    tenant,
    setActive,
    organization?.slug,
    userMemberships.data,
    userInvitations.data,
    userSuggestions.data,
    orgState,
  ]);

  useEffect(() => {
    if (authCorrection === 'set-active') {
      // Force a reload of the current page to purge the store
      // That's because the active organization is not present in the store
      // which means it's not reloaded
      setActive?.({ organization: tenant });
      return;
    }

    if (authCorrection === 'select-org') {
      // User has an invitation to the organization so we can redirect to the
      // organization selection page
      // TODO[redirect]: we should redirect to the current page
      push(PATHS.ORG_SELECTION);
      return;
    }
  }, [authCorrection, push, setActive, tenant]);

  if (!isUserLoaded || !!authCorrection) {
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
          orgState,
        }}
      >
        {children}
      </AuthContext.Provider>
    </AuthUIContext.Provider>
  );
}
