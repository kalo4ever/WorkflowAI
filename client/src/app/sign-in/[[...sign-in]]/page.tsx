'use client';

// Ok here since the route is clerk specific
// eslint-disable-next-line no-restricted-imports
import { SignIn } from '@clerk/nextjs';
import { useParsedSearchParams } from '@/lib/queryString';

export default function Page() {
  const { forceRedirectUrl } = useParsedSearchParams('forceRedirectUrl');

  return (
    <div className='w-full h-full flex items-center justify-center bg-gray-100'>
      <SignIn forceRedirectUrl={forceRedirectUrl} />
    </div>
  );
}
