import Image from 'next/image';
import { cn } from '@/lib/utils';

type CompanyMoneyEntry = {
  imageUrl: string;
  money?: string;
  users?: string;
  width: number;
  height: number;
  url: string;
};

const companiesMoneyEntries: CompanyMoneyEntry[] = [
  {
    imageUrl: 'https://workflowai.blob.core.windows.net/workflowai-public/landing/LandingCompanyLogo5.png',
    money: '$55m',
    width: 125,
    height: 32,
    url: 'https://mygardyn.com/',
  },
  {
    imageUrl: 'https://workflowai.blob.core.windows.net/workflowai-public/landing/LandingCompanyLogo2.png',
    money: '$50m',
    width: 188,
    height: 32,
    url: 'https://www.berrystreet.co',
  },
  {
    imageUrl: 'https://workflowai.blob.core.windows.net/workflowai-public/landing/LandingCompanyLogo1.png',
    money: 'a lot',
    width: 94,
    height: 32,
    url: 'https://www.interfaceai.com',
  },
  {
    imageUrl: 'https://workflowai.blob.core.windows.net/workflowai-public/landing/LandingCompanyLogo3.png',
    money: '$17m',
    width: 78,
    height: 32,
    url: 'https://amo.co',
  },
  {
    imageUrl: 'https://workflowai.blob.core.windows.net/workflowai-public/landing/LandingCompanyLogo4.png',
    width: 80,
    height: 32,
    users: '>800k',
    url: 'https://www.luni.app/',
  },
];

type CompanyMoneyViewProps = {
  companyMoneyEntry: CompanyMoneyEntry;
};

export function CompanyMoneyView(props: CompanyMoneyViewProps) {
  const { companyMoneyEntry } = props;

  return (
    <div
      className='flex flex-col items-center justify-center gap-2 cursor-pointer'
      onClick={() => {
        window.open(companyMoneyEntry.url, '_blank');
      }}
    >
      <Image
        src={companyMoneyEntry.imageUrl}
        alt='company logo'
        width={companyMoneyEntry.width}
        height={companyMoneyEntry.height}
      />
      <div className='bg-white rounded-[2px] px-1 py-[2px] border border-gray-100 font-semibold text-[12px] text-gray-500'>
        {!!companyMoneyEntry.money && companyMoneyEntry.money !== 'a lot' && (
          <>
            Raised <span className='text-gray-700'>{companyMoneyEntry.money}</span>
          </>
        )}
        {companyMoneyEntry.money === 'a lot' && (
          <>
            Raised... <span className='text-gray-700'>a lot</span>
          </>
        )}
        {!!companyMoneyEntry.users && (
          <>
            <span className='text-gray-700'>{companyMoneyEntry.users}</span> users
          </>
        )}
      </div>
    </div>
  );
}

type Props = {
  className?: string;
};

export function CompaniesMoneyComponent(props: Props) {
  const { className } = props;

  return (
    <div className={cn('flex flex-col items-center sm:gap-12 gap-8 sm:px-16 px-4 w-full max-w-[1260px]', className)}>
      <div className='flex flex-wrap w-full justify-center items-center sm:gap-11 gap-4'>
        {companiesMoneyEntries.map((companyMoneyEntry) => (
          <CompanyMoneyView key={companyMoneyEntry.imageUrl} companyMoneyEntry={companyMoneyEntry} />
        ))}
      </div>
    </div>
  );
}
