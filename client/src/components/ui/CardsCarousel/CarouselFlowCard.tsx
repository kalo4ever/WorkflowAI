import { cx } from 'class-variance-authority';
import { VideoComponent } from '@/components/ui/VideoComponent';
import { CardsCarouselEntryContent } from './CarouselCard';

type CarouselFlowCardProgressProps = {
  progress: number;
};

function CarouselFlowCardProgress(props: CarouselFlowCardProgressProps) {
  const { progress } = props;
  return (
    <div className='flex-grow w-0.5 h-full bg-slate-200'>
      <div
        className='flex w-full bg-slate-900'
        style={{
          height: `${progress}%`,
        }}
      ></div>
    </div>
  );
}

type CarouselFlowCardProps = {
  entry: CardsCarouselEntryContent;
  page: number;
  currentPage: number | undefined;
};

export function CarouselFlowCard(props: CarouselFlowCardProps) {
  const { entry, page, currentPage } = props;
  const isSelected = !!currentPage ? page === Math.floor(currentPage) : false;
  const progress = Math.min(Math.max(!!currentPage ? (currentPage - page) * 100 : 0, 0), 100);

  return (
    <div className={`flex flex-col`}>
      <div
        className={cx(
          ' font-medium text-xs px-2 py-1 rounded-full w-fit -ml-2',
          isSelected ? 'text-white bg-slate-900' : 'text-slate-400 bg-white border'
        )}
      >
        {entry.name.toUpperCase()}
      </div>

      <div className='flex flex-row h-full items-stretch'>
        <div className='flex-grow w-6 pl-2 items-stretch'>
          <CarouselFlowCardProgress progress={progress} />
        </div>
        <div className='flex flex-col w-full h-full py-4 gap-4'>
          <div className='text-slate-500 font-light text-base leading-1.5 whitespace-pre-wrap'>{entry.text}</div>

          <VideoComponent
            id={entry.videoSrc}
            src={entry.videoSrc}
            title={entry.name}
            subtitle='4 minutes'
            buttonTitle='Watch the Demo'
            width={entry.videoWidth}
            height={entry.videoHeight}
            autoPlay={true}
            isAutoPlayPaused={!isSelected}
          />
        </div>
      </div>
    </div>
  );
}
