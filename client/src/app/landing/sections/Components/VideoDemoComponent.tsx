import { Stream } from '@cloudflare/stream-react';
import {
  ArrowTrendingRegular,
  ChatRegular,
  ClipboardTaskList16Regular,
  CloudRegular,
  DataUsageRegular,
  ListBarTreeRegular,
} from '@fluentui/react-icons';
import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

type VideoDemo = {
  id: number;
  videoId: string;
  width: number;
  height: number;
  name: string;
  icon: React.ReactNode;
};

const videoDemos: VideoDemo[] = [
  {
    id: 1,
    videoId: 'dd690ad4cea386e49731f843ecfd9b63',
    width: 954,
    height: 566,
    name: 'Describe',
    icon: <ChatRegular className='w-4 h-4' />,
  },
  {
    id: 2,
    videoId: 'd5eb8fa37be6e96aa43990015f1ef5de',
    width: 954,
    height: 566,
    name: 'Compare',
    icon: <DataUsageRegular className='w-4 h-4' />,
  },
  {
    id: 3,
    videoId: 'dd690ad4cea386e49731f843ecfd9b63',
    width: 954,
    height: 566,
    name: 'Deploy',
    icon: <CloudRegular className='w-4 h-4' />,
  },
  {
    id: 4,
    videoId: 'd5eb8fa37be6e96aa43990015f1ef5de',
    width: 954,
    height: 566,
    name: 'Observe',
    icon: <ListBarTreeRegular className='w-4 h-4' />,
  },
  {
    id: 5,
    videoId: 'dd690ad4cea386e49731f843ecfd9b63',
    width: 954,
    height: 566,
    name: 'Improve',
    icon: <ArrowTrendingRegular className='w-4 h-4' />,
  },
  {
    id: 6,
    videoId: 'd5eb8fa37be6e96aa43990015f1ef5de',
    width: 954,
    height: 566,
    name: 'Monitor',
    icon: <ClipboardTaskList16Regular className='w-4 h-4' />,
  },
];

type VideoDemoButtonProps = {
  videoDemo: VideoDemo;
  selectedVideoDemo: VideoDemo;
  setSelectedVideoDemo: (videoDemo: VideoDemo) => void;
};

export function VideoDemoButton(props: VideoDemoButtonProps) {
  const { videoDemo, selectedVideoDemo, setSelectedVideoDemo } = props;

  return (
    <div
      className={cn(
        'flex items-center gap-1 px-2 py-1 rounded-[2px] border border-gray-300 hover:bg-gray-100 cursor-pointer text-gray-800 font-semibold text-[12px]',
        selectedVideoDemo.id === videoDemo.id ? 'bg-gray-200 shadow-inner' : 'bg-white'
      )}
      onClick={() => setSelectedVideoDemo(videoDemo)}
    >
      {videoDemo.icon}
      {videoDemo.name}
    </div>
  );
}

type SingleVideoDemoProps = {
  videoId: string;
  id: number;
  selectedVideoDemoId: number;
};

export function SingleVideoDemoComponent(props: SingleVideoDemoProps) {
  const { videoId, id, selectedVideoDemoId } = props;
  const [shouldReset, setShouldReset] = useState(false);

  const isSelected = id === selectedVideoDemoId;

  useEffect(() => {
    if (isSelected) {
      setShouldReset(true);
      // Reset the flag after a short delay to allow the currentTime to take effect
      const timer = setTimeout(() => setShouldReset(false), 100);
      return () => clearTimeout(timer);
    }
  }, [isSelected]);

  const currentTime = shouldReset || !isSelected ? 0 : undefined;

  return (
    <div
      key={id}
      className='absolute top-0 left-0 flex items-center justify-center w-full h-full'
      style={{ opacity: isSelected ? 1 : 0 }}
    >
      <Stream
        src={videoId}
        controls={false}
        muted={true}
        preload='auto'
        autoplay={true}
        loop={true}
        height='1080'
        width='1920'
        currentTime={currentTime}
        className='w-full h-full rounded-[2px]'
      />
    </div>
  );
}

type Props = {
  className?: string;
};

export function VideoDemoComponent(props: Props) {
  const { className } = props;

  const [selectedVideoDemo, setSelectedVideoDemo] = useState<VideoDemo>(videoDemos[0]);

  return (
    <div className={cn('flex flex-col items-center sm:px-4 px-2 w-full max-w-[1292px] gap-6', className)}>
      <div className='flex flex-wrap w-full justify-center items-center gap-4'>
        {videoDemos.map((videoDemo) => (
          <VideoDemoButton
            key={videoDemo.id}
            videoDemo={videoDemo}
            selectedVideoDemo={selectedVideoDemo}
            setSelectedVideoDemo={setSelectedVideoDemo}
          />
        ))}
      </div>

      <div className='flex w-full h-full border border-gray-200 p-0 rounded-[4px] overflow-hidden'>
        <div className='relative flex w-full overflow-hidden' style={{ paddingTop: '59.3%' }}>
          {videoDemos.map((videoDemo) => (
            <SingleVideoDemoComponent
              key={videoDemo.id}
              videoId={videoDemo.videoId}
              id={videoDemo.id}
              selectedVideoDemoId={selectedVideoDemo.id}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
