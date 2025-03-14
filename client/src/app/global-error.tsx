'use client';

import * as Sentry from '@sentry/nextjs';
import { useEffect } from 'react';
import { Button } from '@/components/ui/Button';

export default function GlobalError({ error }: { error: Error }) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html className='h-full'>
      <body className='h-full w-full flex flex-col items-center justify-center gap-4'>
        <h2>Something went wrong!</h2>
        <Button toRoute='/'>Go back to the home page</Button>
      </body>
    </html>
  );
}
