'use client';

import { useCallback } from 'react';
import { Button } from '@/components/ui/Button';
import { useCopy } from '@/lib/hooks/useCopy';
import { useOrFetchToken } from '@/store';

export default function Page() {
  const copy = useCopy();

  const { token } = useOrFetchToken();

  const copyAction = useCallback(() => {
    if (token) {
      copy(token);
    }
  }, [copy, token]);

  return (
    <div className='flex flex-col gap-2 p-4 items-start'>
      Token
      <code
        className='bg-gray-100 p-4 rounded-md max-w-full break-all'
        onClick={copyAction}
      >
        {token ?? 'Generating...'}
      </code>
      <Button onClick={copyAction}>Copy</Button>
    </div>
  );
}
