import Image from 'next/image';
import InvestorLogo1Src from '@/components/Images/InvestorLogo1.png';
import InvestorLogo2Src from '@/components/Images/InvestorLogo2.png';
import InvestorLogo3Src from '@/components/Images/InvestorLogo3.png';
import InvestorLogo4Src from '@/components/Images/InvestorLogo4.png';
import InvestorLogo5Src from '@/components/Images/InvestorLogo5.png';
import InvestorLogo6Src from '@/components/Images/InvestorLogo6.png';
import { cn } from '@/lib/utils';

const investorLogos = [
  InvestorLogo1Src,
  InvestorLogo2Src,
  InvestorLogo3Src,
  InvestorLogo4Src,
  InvestorLogo5Src,
  InvestorLogo6Src,
];

type InvestorLogosSectionProps = {
  className?: string;
};

export function InvestorLogosSection(props: InvestorLogosSectionProps) {
  const { className } = props;

  return (
    <div className={cn('flex flex-col gap-2 items-center px-4', className)}>
      <div className='text-[16px] font-normal text-gray-500 text-center'>
        Backed by investors from leading brands and companies from across the
        globe
      </div>
      <div className='flex flex-wrap max-w-[1132px] gap-x-4 gap-y-7 pt-8 items-start justify-center'>
        {investorLogos.map((logo) => (
          <Image
            src={logo}
            alt='Investor Logo'
            key={logo.src}
            className='w-[240px] h-[48px]'
          />
        ))}
      </div>
    </div>
  );
}
