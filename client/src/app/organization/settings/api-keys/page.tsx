'use client';

import { ApiKeysModal } from '@/components/ApiKeysModal/ApiKeysModal';

export default function Page() {
  return (
    <div className='flex w-full h-full bg-custom-gradient-1'>
      <ApiKeysModal open={true} closeModal={() => {}} showClose={false} />
    </div>
  );
}
