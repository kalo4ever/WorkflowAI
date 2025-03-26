import { cx } from 'class-variance-authority';
import { CardsCarouselEntryContent } from './CarouselCard';

type HeaderEntryProgressProps = {
  progress: number;
};

function HeaderEntryProgress(props: HeaderEntryProgressProps) {
  const { progress } = props;
  return (
    <div className='flex-grow bg-slate-200 h-0.5 mx-2'>
      <div
        className='flex h-full bg-slate-900'
        style={{
          width: `${progress}%`,
        }}
      ></div>
    </div>
  );
}

type CardsCarouselHeaderEntryProps = {
  card: CardsCarouselEntryContent;
  page: number;
  index: number;
  showConnection: boolean;
};

function CardsCarouselHeaderEntry(props: CardsCarouselHeaderEntryProps) {
  const { card, page, index, showConnection } = props;

  const isSelected = index <= Math.floor(page);
  const progress = Math.max(Math.min(page - index, 1), 0) * 100;

  return (
    <div className={cx('flex flex-row items-center', showConnection && 'w-full')}>
      <div
        className={cx(
          'rounded-full px-2 py-1 font-medium text-xs',
          isSelected ? 'bg-slate-900 text-white' : 'border border-slate-200 text-slate-400'
        )}
      >
        {card.name.toUpperCase()}
      </div>
      {showConnection && <HeaderEntryProgress progress={progress} />}
    </div>
  );
}

type CardsCarouselHeaderProps = {
  cardContent: CardsCarouselEntryContent[];
  page: number;
};

export function CardsCarouselHeader(props: CardsCarouselHeaderProps) {
  const { cardContent, page } = props;
  return (
    <div className='flex flex-row justify-between'>
      {cardContent.map((card, index) => (
        <CardsCarouselHeaderEntry
          key={index}
          card={card}
          page={page}
          index={index}
          showConnection={index !== cardContent.length - 1}
        />
      ))}
    </div>
  );
}
