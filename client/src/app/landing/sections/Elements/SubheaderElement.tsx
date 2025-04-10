import Image from 'next/image';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { HeaderEntry } from '../StaticData/LandingStaticData';

type Props = {
  entry: HeaderEntry;
  routeForSignUp?: string;
};

export function SubheaderElement(props: Props) {
  const { entry, routeForSignUp } = props;

  return (
    <div className='flex flex-col gap-4 w-full items-center'>
      {!!entry.logoURL && !!entry.logoWidth && !!entry.logoHeight && (
        <Image
          src={entry.logoURL}
          alt='logo'
          width={entry.logoWidth}
          height={entry.logoHeight}
          className={cn('mb-8', entry.logoLink && 'cursor-pointer')}
          onClick={(event) => {
            if (entry.logoLink) {
              event.stopPropagation();
              window.open(entry.logoLink, '_blank');
            }
          }}
        />
      )}
      <div
        className={cn(
          'flex w-full items-center justify-center text-center text-gray-900 font-semibold sm:text-[30px] text-[24px]',
          entry.titleSizeClassName ?? 'sm:text-[30px] text-[24px]'
        )}
      >
        {entry.title}
      </div>
      {entry.description && (
        <div
          className={cn(
            'flex w-fit items-center justify-center text-center text-gray-500 font-normal sm:text-[20px] text-[16px] whitespace-pre-wrap',
            entry.descriptionMaxWidth
          )}
        >
          {entry.description}
        </div>
      )}
      {entry.buttonText && (
        <Button
          variant={entry.buttonVariant ?? 'newDesignGray'}
          toRoute={entry.url === 'SignUp' ? routeForSignUp : entry.url}
          icon={!!entry.buttonIcon && <Image src={entry.buttonIcon} alt='Icon' className='w-4 h-4' />}
          openInNewTab={true}
        >
          {entry.buttonText}
        </Button>
      )}
    </div>
  );
}
