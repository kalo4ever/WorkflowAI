'use client';

// eslint-disable-next-line no-restricted-imports
import { useOrganizationList } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Loader } from '@/components/ui/Loader';
import { stringifyQueryParams, useParsedSearchParams } from '@/lib/queryString';
import { PATHS } from '@/lib/routeFormatter';

export default function SignUpRedirectPage() {
  const { userInvitations, userMemberships, userSuggestions, isLoaded } = useOrganizationList({
    userMemberships: true,
    userInvitations: true,
    userSuggestions: true,
  });

  const { redirectUrl } = useParsedSearchParams('redirectUrl');
  const { replace } = useRouter();

  useEffect(() => {
    if (!isLoaded) {
      return;
    }

    if (userInvitations.data?.length || userMemberships.data?.length || userSuggestions.data?.length) {
      replace(PATHS.ORG_SELECTION + stringifyQueryParams({ redirectUrl }));
      return;
    }

    replace(redirectUrl ?? '/');
  }, [userInvitations.data, userMemberships.data, userSuggestions.data, replace, isLoaded, redirectUrl]);

  return (
    <div className='w-full h-full flex items-center justify-center bg-gray-100'>
      <Loader />
    </div>
  );
}
