import Image from 'next/image';
import { useCallback, useMemo } from 'react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { QuoteElement } from '../Elements/QuoteElement';
import { FeatureEntry } from '../StaticData/LandingStaticData';

type FeatureCardProps = {
  entry: FeatureEntry;
  scrollToSuggestedFeatures?: () => void;
};

function FeatureCard(props: FeatureCardProps) {
  const { entry, scrollToSuggestedFeatures } = props;

  const onClick = useCallback(() => {
    if (!entry.url) {
      return;
    }

    switch (entry.url) {
      case 'ScrollToSuggestedFeatures':
        if (scrollToSuggestedFeatures) {
          scrollToSuggestedFeatures();
        }
        break;
      default:
        window.open(entry.url, '_blank');
    }
  }, [entry.url, scrollToSuggestedFeatures]);

  return (
    <div className='flex flex-col border border-gray-200 rounded-[2px] bg-custom-gradient-1'>
      <div
        className={cn(
          'flex flex-col',
          entry.url && 'cursor-pointer',
          !!entry.showImageWithoutPadding ? 'p-0' : 'sm:p-6 p-4'
        )}
        onClick={onClick}
      >
        <Image
          src={entry.imageSrc}
          alt={entry.title ?? 'Image'}
          width={entry.imageWidth ?? 458}
          height={entry.imageHeight ?? 232}
          className={cn('flex w-full', !!entry.showImageWithoutPadding ? 'mb-0' : 'mb-6')}
        />
        {!!entry.title && (
          <div className='sm:text-[18px] text-[16px] font-semibold text-gray-900 pb-1'>{entry.title}</div>
        )}
        {!!entry.description && (
          <div className='sm:text-[16px] text-[13px] font-normal text-gray-500'>{entry.description}</div>
        )}
        {entry.buttonText && (
          <div className='flex justify-start mt-6'>
            <Button variant='newDesignGray'>{entry.buttonText}</Button>
          </div>
        )}
      </div>
      {entry.qoute && (
        <div className={cn('flex w-full h-full sm:p-6 p-4', !!entry.title && 'mt-6 border-t border-gray-200')}>
          <QuoteElement entry={entry.qoute} />
        </div>
      )}
    </div>
  );
}

type Props = {
  className?: string;
  entries: FeatureEntry[];
  scrollToSuggestedFeatures?: () => void;
  showThreeColumns?: boolean;
};

export function GridComponent(props: Props) {
  const { entries, scrollToSuggestedFeatures, showThreeColumns = false, className } = props;

  const innerClassName = useMemo(() => {
    if (showThreeColumns) {
      return 'grid w-full grid-cols-1 sm:grid-cols-3 gap-6';
    }
    return 'grid w-full grid-cols-1 sm:grid-cols-2 gap-6';
  }, [showThreeColumns]);

  return (
    <div className={cn('flex items-center sm:px-16 px-4 w-full max-w-[1260px]', className)}>
      <div className={innerClassName}>
        {entries.map((feature) => (
          <FeatureCard entry={feature} key={feature.title} scrollToSuggestedFeatures={scrollToSuggestedFeatures} />
        ))}
      </div>
    </div>
  );
}
