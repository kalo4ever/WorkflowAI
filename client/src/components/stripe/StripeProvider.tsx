'use client';

import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { ReactNode } from 'react';
import { STRIPE_PUBLISHABLE_KEY } from '@/lib/constants';

const stripePromise = loadStripe(STRIPE_PUBLISHABLE_KEY ?? '');

export function StripeProvider({ children }: { children: ReactNode }) {
  return (
    <Elements
      stripe={stripePromise}
      options={{
        appearance: {
          disableAnimations: true,
          theme: 'stripe',
          variables: {
            fontFamily: 'Lato, system-ui, sans-serif',
            borderRadius: '2px',
            colorBackground: 'white',
            fontSizeBase: '14px',
            focusBoxShadow: '0',
            focusOutline: '0',
            colorPrimary: 'black',
            colorText: '#111827',
          },
          labels: 'floating',
        },
      }}
    >
      {children}
    </Elements>
  );
}
