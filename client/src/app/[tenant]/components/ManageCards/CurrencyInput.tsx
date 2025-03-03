import { useCallback, useState } from 'react';
import { Input } from '@/components/ui/Input';

interface CurrencyInputProps {
  amount: number | undefined;
  setAmount: (amount: number | undefined) => void;
}

export function CurrencyInput(props: CurrencyInputProps) {
  const { amount, setAmount } = props;
  const [isFocused, setIsFocused] = useState(false);

  const updateAmount = useCallback(
    (text: string) => {
      if (!text) {
        setAmount(undefined);
        return;
      }
      const amount = Number(text);
      setAmount(Number.isNaN(amount) ? undefined : amount);
    },
    [setAmount]
  );

  return (
    <div className='relative'>
      <span
        className={`absolute left-3 top-1/2 -translate-y-1/2 pt-[1px] text-[13px] font-normal ${isFocused || !!amount ? 'text-gray-900' : 'text-gray-400'}`}
      >
        $
      </span>
      <Input
        type='number'
        value={amount ?? ''}
        onChange={(e) => updateAmount(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        className='pl-[21px] text-[13px] font-normal text-gray-900'
      />
    </div>
  );
}
