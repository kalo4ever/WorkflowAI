import { ReactNode } from 'react';
import { STRIPE_PUBLISHABLE_KEY } from '@/lib/constants';
import { StripeProvider } from './StripeProvider';

export function StripeWrapper({ children }: { children: ReactNode }) {
  if (STRIPE_PUBLISHABLE_KEY) {
    return <StripeProvider>{children}</StripeProvider>;
  }
  return <>{children}</>;
}
