'use client';

import { XCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/components/ui/use-toast';

export default function PaymentCancelPage() {
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    toast({
      title: 'Payment Cancelled',
      description: 'Your payment was cancelled. No charges were made.',
      variant: 'destructive',
    });
  }, [toast]);

  return (
    <div className='flex flex-col items-center justify-center min-h-[60vh] gap-6'>
      <div className='flex flex-col items-center gap-2 text-center'>
        <XCircle className='h-12 w-12 text-red-500' />
        <h1 className='text-2xl font-semibold'>Payment Cancelled</h1>
        <p className='text-muted-foreground'>Your payment was cancelled. No charges were made.</p>
      </div>
      <Button onClick={() => router.push('/')}>Return to Dashboard</Button>
    </div>
  );
}
