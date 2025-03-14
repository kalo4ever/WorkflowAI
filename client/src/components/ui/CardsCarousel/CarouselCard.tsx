import { VideoComponent } from '@/components/ui/VideoComponent';

export type CardsCarouselEntryContent = {
  name: string;
  text: string;
  videoSrc: string;
  videoHeight: number;
  videoWidth: number;
};

type CarouselCardProps = {
  entry: CardsCarouselEntryContent;
  width?: number;
  isSelected?: boolean;
};

export function CarouselCard(props: CarouselCardProps) {
  const { entry, width, isSelected } = props;
  return (
    <div
      className={`flex flex-col gap-8 sm:gap-9 p-6 sm:p-8 bg-white rounded-[28px] border justify-between`}
      style={{
        width: width ? `${width}px` : undefined,
      }}
    >
      <div className='text-slate-500 font-light text-lg sm:text-xl leading-[28px] sm:leading-[32px] whitespace-pre-wrap'>
        <span className='text-slate-900 font-medium'>{entry.name}.</span>{' '}
        {entry.text}
      </div>

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
  );
}
