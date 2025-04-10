import { Stream } from '@cloudflare/stream-react';
import {
  ChatRegular,
  ClipboardTaskList16Regular,
  CloudRegular,
  DataUsageRegular,
  ListBarTreeRegular,
  PlayCircleRegular,
} from '@fluentui/react-icons';
import { useState } from 'react';
import { cn } from '@/lib/utils';

type VideoDemo = {
  id: number;
  videoId: string;
  name: string;
  icon: React.ReactNode;
};

const videoDemos: VideoDemo[] = [
  {
    id: 1,
    videoId: 'c118e79228b019f3d95228bbf236b563',
    name: 'Describe',
    icon: <ChatRegular className='w-4 h-4' />,
  },
  {
    id: 2,
    videoId: 'c118e79228b019f3d95228bbf236b563',
    name: 'Compare',
    icon: <DataUsageRegular className='w-4 h-4' />,
  },
  {
    id: 3,
    videoId: 'c118e79228b019f3d95228bbf236b563',
    name: 'Deploy',
    icon: <CloudRegular className='w-4 h-4' />,
  },
  {
    id: 4,
    videoId: 'c118e79228b019f3d95228bbf236b563',
    name: 'Observe',
    icon: <ListBarTreeRegular className='w-4 h-4' />,
  },
  {
    id: 5,
    videoId: 'c118e79228b019f3d95228bbf236b563',
    name: 'Improve',
    icon: <PlayCircleRegular className='w-4 h-4' />,
  },
  {
    id: 6,
    videoId: 'c118e79228b019f3d95228bbf236b563',
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

type Props = {
  className?: string;
};

export function VideoDemoComponent(props: Props) {
  const { className } = props;

  const [selectedVideoDemo, setSelectedVideoDemo] = useState<VideoDemo>(videoDemos[0]);

  return (
    <div className={cn('flex flex-col items-center sm:px-16 px-4 w-full max-w-[1040px] gap-6', className)}>
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

      <div className='flex w-full h-full border border-gray-100 bg-white p-4 rounded-[4px] overflow-hidden'>
        <div className='flex w-full h-full rounded-[2px] border border-gray-200'>
          <div className='relative w-full' style={{ paddingTop: '56.25%' }}>
            {videoDemos.map((videoDemo) => (
              <div
                key={videoDemo.id}
                className={cn(
                  'absolute top-0 left-0 w-full h-full',
                  selectedVideoDemo.id === videoDemo.id ? 'opacity-100' : 'opacity-0'
                )}
              >
                <Stream
                  src={videoDemo.videoId}
                  controls={false}
                  muted={true}
                  preload='auto'
                  autoplay={true}
                  loop={true}
                  className='w-full h-full rounded-[2px]'
                  height='1080'
                  width='1920'
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
