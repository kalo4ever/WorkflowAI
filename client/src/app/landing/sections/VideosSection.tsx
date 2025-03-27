import { Stream } from '@cloudflare/stream-react';
import Image from 'next/image';
import { cn } from '@/lib/utils';
import { SectionSeparator } from './SectionSeparator';

export type VideoEntry = {
  title: string;
  description: string;
  videoId: string;
  quote: string;
  authorImageSrc: string;
  quoteAuthor: string;
  authorsPosition: string;
  authorsCompany: string;
  companyURL: string;
};

type VideosSectionProps = {
  className?: string;
  videos: VideoEntry[];
};

export function VideosSection(props: VideosSectionProps) {
  const { className, videos } = props;

  return (
    <div className={cn('flex flex-col items-center px-16 w-full max-w-[1260px]', className)}>
      {videos.map((video, index) => (
        <div key={video.videoId} className='flex flex-col w-full items-center'>
          <div key={video.videoId} className='flex flex-col gap-8 w-full items-center'>
            <div className='flex flex-col gap-2 w-full items-center'>
              <div className='flex w-full items-center justify-center text-center text-gray-900 font-medium text-[30px]'>
                {video.title}
              </div>
              <div className='flex w-full items-center justify-center text-center text-gray-500 font-normal text-[16px]'>
                {video.description}
              </div>
            </div>
            <div className='w-full max-w-[1132px]'>
              <Stream
                src={video.videoId}
                controls
                autoplay={false}
                muted={false}
                loop={false}
                className='w-full h-full rounded-[2px]'
              />
            </div>
            <div className='flex flex-col gap-8 w-full items-center max-w-[1000px]'>
              <div className='flex w-full items-center justify-center text-center text-gray-500 font-normal text-[20px]'>
                {video.quote}
              </div>
              <div className='flex flex-col gap-2 w-full items-center'>
                <Image
                  src={video.authorImageSrc}
                  alt='Person'
                  key={video.authorImageSrc}
                  className='object-cover w-10 h-10 rounded-full'
                  width={40}
                  height={40}
                />
                <div className='flex flex-col w-full items-center'>
                  <div className='flex w-full items-center justify-center text-center text-gray-700 font-semibold text-[16px]'>
                    {video.quoteAuthor}
                  </div>
                  <div className='flex w-full items-center justify-center text-center text-gray-500 font-normal text-[16px]'>
                    {video.authorsPosition} at
                    <a href={video.companyURL} className='underline ml-1' target='_blank'>
                      {video.authorsCompany}
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
          {index !== videos.length - 1 && <SectionSeparator className='mt-[80px] mb-[80px]' />}
        </div>
      ))}
    </div>
  );
}
