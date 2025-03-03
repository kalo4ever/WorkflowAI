'use client';

// Ok here since the route is clerk specific
// eslint-disable-next-line no-restricted-imports
import {
  CreateOrganization,
  OrganizationList,
  RedirectToSignIn,
  useOrganization,
  useOrganizationList,
  useUser,
} from '@clerk/nextjs';
import { OrganizationResource, UserResource } from '@clerk/types';
import { captureException } from '@sentry/nextjs';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Loader } from '@/components/ui/Loader';
import { tasksRoute } from '@/lib/routeFormatter';
import { TenantID } from '@/types/aliases';

async function shouldDisplaySelectOrganization(user: UserResource) {
  if (user.organizationMemberships.length > 0) {
    return true;
  }
  const [invitations, suggestions] = await Promise.all([
    user.getOrganizationInvitations(),
    user.getOrganizationSuggestions(),
  ]);

  return invitations.data.length > 0 || suggestions.data.length > 0;
}

function postSelectOrganizationURL(org: OrganizationResource) {
  return tasksRoute(org.slug as TenantID);
}

export default function OrgSelectionPage() {
  const { user, isLoaded: isUserLoaded } = useUser();
  const { organization, isLoaded: isOrganizationLoaded } = useOrganization();
  const {
    isLoaded: areOrganizationsLoaded,
    setActive,
    userMemberships,
  } = useOrganizationList({
    userMemberships: {
      infinite: true,
    },
  });
  const router = useRouter();

  const [shouldDisplayOrgSwitcher, setShouldDisplayOrgSwitcher] =
    useState<boolean>();

  useEffect(() => {
    if (!user) return;

    shouldDisplaySelectOrganization(user)
      .then(setShouldDisplayOrgSwitcher)
      .catch((e) => {
        // Fallback to false if we can't determine the result
        captureException(e);
        setShouldDisplayOrgSwitcher(false);
      });
  }, [user]);

  const isLoaded =
    isUserLoaded &&
    isOrganizationLoaded &&
    areOrganizationsLoaded &&
    shouldDisplayOrgSwitcher !== undefined;
  const shouldRedirect =
    !!organization ||
    (!!userMemberships?.data && userMemberships?.data?.length > 0);

  useEffect(() => {
    if (shouldRedirect) {
      if (!!organization) {
        router.push(tasksRoute(organization.slug as TenantID));
      } else if (
        setActive &&
        !!userMemberships?.data &&
        userMemberships?.data?.length > 0
      ) {
        const orgId = userMemberships?.data[0].organization.id;
        if (orgId) {
          setActive({ organization: orgId });
        }
      }
    }
  }, [organization, router, setActive, shouldRedirect, userMemberships]);

  if (isUserLoaded && !user) {
    return <RedirectToSignIn />;
  }

  if (!isLoaded || shouldRedirect) {
    return <Loader centered />;
  }

  return (
    <div className='h-full w-full flex items-center justify-center'>
      {shouldDisplayOrgSwitcher ? (
        <OrganizationList
          hidePersonal
          afterSelectOrganizationUrl={postSelectOrganizationURL}
          afterCreateOrganizationUrl={postSelectOrganizationURL}
        />
      ) : (
        <CreateOrganization />
      )}
    </div>
  );
}
