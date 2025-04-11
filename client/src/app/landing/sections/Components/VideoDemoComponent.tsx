import { Stream } from '@cloudflare/stream-react';
import {
  ArrowTrendingRegular,
  ChatRegular,
  ClipboardTaskList16Regular,
  CloudRegular,
  DataUsageRegular,
  ListBarTreeRegular,
} from '@fluentui/react-icons';
import { useCallback, useEffect, useState } from 'react';
import { useToggle } from 'usehooks-ts';
import { cn } from '@/lib/utils';

type VideoDemo = {
  id: number;
  videoSrc: string;
  width: number;
  height: number;
  name: string;
  icon: React.ReactNode;
};

const videoDemos: VideoDemo[] = [
  {
    id: 0,
    videoSrc: '6dd8ba57257c1bbaa870f49a36d256ac',
    width: 1280,
    height: 720,
    name: 'Describe',
    icon: <ChatRegular className='w-4 h-4' />,
  },
  {
    id: 1,
    videoSrc: '28d15ef03f8069f31bc1aa12dd848208',
    width: 1280,
    height: 720,
    name: 'Compare',
    icon: <DataUsageRegular className='w-4 h-4' />,
  },
  {
    id: 2,
    videoSrc: 'd9b84a67c09a218f7f777459f5a7c355',
    width: 1280,
    height: 720,
    name: 'Deploy',
    icon: <CloudRegular className='w-4 h-4' />,
  },
  {
    id: 3,
    videoSrc: '7d8a1b00e3d10b657c3910330ae83953',
    width: 1280,
    height: 720,
    name: 'Observe',
    icon: <ListBarTreeRegular className='w-4 h-4' />,
  },
  {
    id: 4,
    videoSrc: '9983b7e0b7bca28ced765af6a74a5313',
    width: 1280,
    height: 720,
    name: 'Improve',
    icon: <ArrowTrendingRegular className='w-4 h-4' />,
  },
  {
    id: 5,
    videoSrc: '0fb363416b744eaf3a269780148fcc0f',
    width: 1280,
    height: 720,
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
  videoSrc: string;
  videoDemoId: number;
  selectedVideoDemoId: number;
  rewind: boolean;
};

export function SingleVideoDemoComponent(props: SingleVideoDemoProps) {
  const { videoSrc: videoId, videoDemoId: id, selectedVideoDemoId, rewind } = props;
  const [shouldReset, setShouldReset] = useState(false);

  const isSelected = id === selectedVideoDemoId;

  useEffect(() => {
    if (isSelected) {
      setShouldReset(true);
      // Reset the flag after a short delay to allow the currentTime to take effect
      const timer = setTimeout(() => setShouldReset(false), 100);
      return () => clearTimeout(timer);
    }
  }, [isSelected, rewind]);

  const currentTime = shouldReset || !isSelected ? 0 : undefined;

  const [isInFront, setIsInFront] = useState(false);

  useEffect(() => {
    setIsInFront(isSelected);
  }, [isSelected]);

  return (
    <div
      key={id}
      className='absolute top-0 left-0 flex items-center justify-center w-full h-full'
      style={{ zIndex: isInFront ? 10 : id }}
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
  const [rewind, setRewind] = useToggle(false);

  const updateSelectedVideoDemo = useCallback(
    (videoDemo: VideoDemo) => {
      if (videoDemo.id === selectedVideoDemo.id) {
        setRewind();
        return;
      }
      setSelectedVideoDemo(videoDemo);
    },
    [selectedVideoDemo, setSelectedVideoDemo, setRewind]
  );

  return (
    <div className={cn('flex flex-col items-center sm:px-4 px-2 w-full max-w-[1292px] gap-6', className)}>
      <div className='flex flex-wrap w-full justify-center items-center gap-4'>
        {videoDemos.map((videoDemo) => (
          <VideoDemoButton
            key={videoDemo.id}
            videoDemo={videoDemo}
            selectedVideoDemo={selectedVideoDemo}
            setSelectedVideoDemo={updateSelectedVideoDemo}
          />
        ))}
      </div>

      <div className='flex w-full h-full border border-gray-200 p-0 rounded-[4px] overflow-hidden'>
        <div className='relative flex w-full overflow-hidden' style={{ paddingTop: '58.9%' }}>
          {videoDemos.map((videoDemo) => (
            <SingleVideoDemoComponent
              key={videoDemo.id}
              videoSrc={videoDemo.videoSrc}
              videoDemoId={videoDemo.id}
              selectedVideoDemoId={selectedVideoDemo.id}
              rewind={rewind}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
