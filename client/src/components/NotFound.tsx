import { AlertTriangle } from 'lucide-react';
import Error from 'next/error';
import { useLoggedInTenantID } from '@/lib/hooks/useTaskParams';
import { signUpRoute } from '@/lib/routeFormatter';
import { useOrganizationBySlug } from '@/store/organization_by_slug';
import { TenantID } from '@/types/aliases';

export function NotFound() {
  return <Error statusCode={404} withDarkMode={false} />;
}

type NotFoundForNotMatchingTenantProps = {
  tenant: TenantID;
};

export function NotFoundForNotMatchingTenant(
  props: NotFoundForNotMatchingTenantProps
) {
  const { tenant } = props;
  const routeForSignUp = signUpRoute();
  const loggedInTenant = useLoggedInTenantID();

  const { organization } = useOrganizationBySlug(tenant);
  const nameToShow = !!organization?.name ? organization?.name : tenant;

  return (
    <div className='flex w-full h-full items-center justify-center'>
      <div className='flex flex-col gap-6 items-center justify-center'>
        <AlertTriangle className='w-[72px] h-[72px] text-slate-300' />
        <div className='text-base text-slate-500 font-medium text-center max-w-[480px] px-4'>
          {!!loggedInTenant ? (
            <div>
              This page belongs to {nameToShow} and is private.
              <br />
              If you believe you should have access, please double-check that
              you&apos;re logged into the correct account or contact a member of{' '}
              {nameToShow}
            </div>
          ) : (
            <div>
              If you&apos;re part of {nameToShow}, please{' '}
              <a
                href={routeForSignUp}
                className='underline hover:opacity-80 transition-opacity'
              >
                Log In
              </a>{' '}
              to view page.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
