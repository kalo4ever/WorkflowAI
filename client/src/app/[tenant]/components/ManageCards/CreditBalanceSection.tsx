import { formatCurrency } from '@/lib/formatters/numberFormatters';

type CreditBalanceSectionProps = {
  balance: number;
};

export function CreditBalanceSection(props: CreditBalanceSectionProps) {
  const { balance } = props;
  return (
    <div className='flex flex-col px-4 py-3 w-full'>
      <div className='text-[12px] font-median text-gray-900'>
        Credits Balance
      </div>
      <div className='text-[18px] font-semibold text-gray-900'>
        {formatCurrency(balance)}
      </div>
    </div>
  );
}
