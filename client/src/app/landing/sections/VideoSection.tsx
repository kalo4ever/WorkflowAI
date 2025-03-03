import { PlayFilled } from '@fluentui/react-icons';
import Image from 'next/image';
import { Button } from '@/components/ui/Button';
import { SimpleTooltip } from '@/components/ui/Tooltip';
import { cn } from '@/lib/utils';

type VideoSectionProps = {
  className?: string;
};

export function VideoSection(props: VideoSectionProps) {
  const { className } = props;

  return (
    <div
      className={cn(
        'flex w-full px-[24px] items-start justify-center pb-[56px] relative overflow-clip',
        className
      )}
    >
      <div className='flex w-full max-w-[1200px] h-[calc(50vw-24px)] max-h-[600px] bg-white rounded-[4px] border border-gray-300 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)] overflow-clip'>
        <Image
          src={
            'https://workflowai.blob.core.windows.net/workflowai-public/landing.png'
          }
          alt='Landing Page Video Thumbnail'
          className='w-full h-full object-cover opacity-60'
          width={1200}
          height={600}
        />
      </div>
      <div className='absolute bottom-1 left-1 right-1 h-full bg-gradient-to-t from-white/90 to-transparent' />
      <SimpleTooltip content='Demo coming soon!' tooltipDelay={100}>
        <Button
          variant='newDesignIndigo'
          icon={<PlayFilled className='w-5 h-5' />}
          className='absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-[calc(50%+28px)]'
        >
          Watch Demo
        </Button>
      </SimpleTooltip>
    </div>
  );
}
