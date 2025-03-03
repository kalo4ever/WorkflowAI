'use client';

import { Link16Regular } from '@fluentui/react-icons';
import { Button } from '@/components/ui/Button';
import { useCopyCurrentUrl } from '@/lib/hooks/useCopy';

export function CopyUrlButton() {
  const copyUrl = useCopyCurrentUrl();
  return (
    <Button
      variant='newDesign'
      icon={<Link16Regular />}
      onClick={copyUrl}
      className='w-9 h-9 px-0 py-0'
    />
  );
}
