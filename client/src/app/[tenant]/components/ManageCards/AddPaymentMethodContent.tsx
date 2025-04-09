import { AddressElement, CardElement, useElements, useStripe } from '@stripe/react-stripe-js';
import { useCallback, useState } from 'react';
import { BottomButtonBar } from './BottomButtonBar';
import { useStripePayments } from './hooks/useStripePayments';

type AddPaymentMethodContentProps = {
  setIsOpen: (isOpen: boolean) => void;
};

export function AddPaymentMethodContent(props: AddPaymentMethodContentProps) {
  const { setIsOpen } = props;

  const [isLoading, setIsLoading] = useState(false);

  const stripe = useStripe();
  const elements = useElements();

  const { createPaymentMethod } = useStripePayments();

  const handleSubmit = useCallback(
    async (e?: React.FormEvent) => {
      e?.preventDefault();
      if (!stripe || !elements) return;

      setIsLoading(true);

      try {
        await createPaymentMethod(elements);
        setIsOpen(false);
      } catch (error) {
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    },
    [createPaymentMethod, elements, setIsOpen, stripe]
  );

  return (
    <div className='flex flex-col h-full w-full overflow-hidden bg-custom-gradient-1 rounded-[2px]'>
      <div className='text-[16px] font-semibold text-gray-900 px-4 py-3.5 border-b border-gray-200 border-dashed'>
        Add Payment Method
      </div>

      <form onSubmit={handleSubmit}>
        <div className='flex flex-col px-6 py-4'>
          <div className='text-gray-700 font-normal text-[13px]'>Add your card details below</div>
          <div className='text-gray-500 font-normal text-[12px]'>
            This card will be save to your account and can be removed at any time
          </div>
        </div>

        <div className='flex flex-col px-6 pb-4 pt-2 gap-2'>
          <div className='text-gray-900 font-medium text-[13px]'>Card Information</div>
          <CardElement className='py-3 px-2 border border-gray-200 rounded-[2px] bg-white text-gray-900 font-lato text-[13px]' />
        </div>

        <div className='flex flex-col px-6 pb-4 pt-2 gap-2'>
          <div className='text-gray-900 font-medium text-[13px]'>Billing Address</div>
          <AddressElement options={{ mode: 'billing' }} className='font-light text-[13px]' />
        </div>

        <BottomButtonBar
          type='submit'
          actionText='Add Payment Method'
          onCancel={() => setIsOpen(false)}
          onAction={handleSubmit}
          isActionDisabled={!stripe || !elements || isLoading}
        />
      </form>
    </div>
  );
}
