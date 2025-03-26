'use client';

import { CheckCircle2 } from 'lucide-react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/components/ui/use-toast';

export default function PaymentSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (sessionId) {
      toast({
        title: 'Payment Successful',
        description: 'Your credits have been added to your account.',
      });
    }
  }, [searchParams, toast]);

  return (
    <div className='flex flex-col items-center justify-center min-h-[60vh] gap-6'>
      <div className='flex flex-col items-center gap-2 text-center'>
        <CheckCircle2 className='h-12 w-12 text-green-500' />
        <h1 className='text-2xl font-semibold'>Payment Successful</h1>
        <p className='text-muted-foreground'>Your credits have been added to your account</p>
      </div>
      <Button onClick={() => router.push('/')}>Return to Dashboard</Button>
    </div>
  );
}
