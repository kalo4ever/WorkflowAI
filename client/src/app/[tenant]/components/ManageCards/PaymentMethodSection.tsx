import {
  DeleteRegular,
  MoreVerticalRegular,
  PaymentRegular,
} from '@fluentui/react-icons';
import { useCallback, useEffect, useRef, useState } from 'react';
import { AlertDialog } from '@/components/ui/AlertDialog';
import { Button } from '@/components/ui/Button';
import { PaymentMethodResponse } from '@/types/workflowAI';

type PaymentMethodSectionProps = {
  paymentMethod: PaymentMethodResponse | undefined;
  addPaymentMethod: () => void;
  deletePaymentMethod: () => Promise<void>;
};

export function PaymentMethodSection(props: PaymentMethodSectionProps) {
  const { paymentMethod, addPaymentMethod, deletePaymentMethod } = props;
  const [showMenu, setShowMenu] = useState(false);
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false);
      }
    }

    document.addEventListener('mouseup', handleClickOutside);
    return () => {
      document.removeEventListener('mouseup', handleClickOutside);
    };
  }, []);

  const toggleMenu = (event: React.MouseEvent) => {
    event.stopPropagation();
    setShowMenu(!showMenu);
  };

  const onShowDeleteConfirmation = useCallback((event: React.MouseEvent) => {
    event.stopPropagation();
    setShowMenu(false);
    setShowDeleteConfirmation(true);
  }, []);

  const onConfirm = useCallback(async () => {
    await deletePaymentMethod();
    setShowDeleteConfirmation(false);
  }, [deletePaymentMethod]);

  return (
    <div className='flex flex-col gap-2 px-4 pt-1 pb-2'>
      <div className='text-[13px] font-medium text-gray-900'>
        Payment Method
      </div>
      {paymentMethod?.payment_method_id ? (
        <div className='flex flex-row gap-4 py-3 px-4 border border-gray-200 items-center relative'>
          <div className='flex rounded-full bg-gray-100 w-10 h-10 items-center justify-center'>
            <PaymentRegular className='w-5 h-5 text-gray-900' />
          </div>
          <div className='flex flex-col gap-0.5 h-fit flex-grow'>
            <div className='text-[13px] font-semibold text-gray-700'>
              ••••{paymentMethod.last4}
            </div>
            <div className='text-[12px] font-normal text-gray-500'>
              Expires {paymentMethod.exp_month}/{paymentMethod.exp_year}
            </div>
          </div>
          <div className='relative' ref={menuRef}>
            <Button
              variant='newDesignGray'
              size='none'
              className='w-7 h-7'
              onClick={toggleMenu}
            >
              <MoreVerticalRegular className='w-4 h-4 text-gray-800 flex-shrink-0' />
            </Button>
            {showMenu && (
              <div className='absolute right-0 top-full mt-1 z-10'>
                <Button
                  variant='newDesign'
                  size='none'
                  icon={<DeleteRegular className='w-4 h-4 text-red-700' />}
                  className='shadow-lg text-red-700 font-normal text-[13px] px-[10px] py-[6px]'
                  onClick={onShowDeleteConfirmation}
                >
                  Delete
                </Button>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div>
          <Button variant='newDesignIndigo' onClick={addPaymentMethod}>
            Add Payment Method
          </Button>
        </div>
      )}
      <AlertDialog
        open={showDeleteConfirmation}
        title={'Delete Payment Method'}
        text={
          'Automatic Recharge will be automatically disabled and you will not be able to add credits until a new payment method is connected.'
        }
        confrimationText='Delete Payment Method'
        destructive={true}
        onCancel={() => setShowDeleteConfirmation(false)}
        onConfirm={onConfirm}
      />
    </div>
  );
}
