'use client';

// Ok here since the route is clerk specific
// eslint-disable-next-line no-restricted-imports
import { SignUp } from '@clerk/nextjs';
import { useParsedSearchParams } from '@/lib/queryString';
import { signUpRedirectRoute } from '@/lib/routeFormatter';

export default function Page() {
  const { forceRedirectUrl } = useParsedSearchParams('forceRedirectUrl');

  return (
    <div className='w-full h-full flex items-center justify-center bg-gray-100'>
      <SignUp forceRedirectUrl={signUpRedirectRoute(forceRedirectUrl)} />
    </div>
  );
}
