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
    <div className={cn('flex flex-col items-center sm:px-16 px-4 w-full max-w-[1260px]', className)}>
      {videos.map((video, index) => (
        <div key={video.videoId} className='flex flex-col w-full items-center'>
          <div key={video.videoId} className='flex flex-col gap-8 w-full items-center h-full overflow-y-hidden'>
            <div className='flex flex-col gap-2 w-fit h-fit items-center'>
              <div className='flex w-fit items-center justify-center text-center text-gray-900 font-medium sm:text-[30px] text-[24px]'>
                {video.title}
              </div>
              <div className='flex w-fit items-center justify-center text-center text-gray-500 font-normal text-[16px]'>
                {video.description}
              </div>
            </div>
            <div className='flex max-w-[1000px] w-full overflow-hidden items-center justify-center'>
              <Stream
                src={video.videoId}
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
            <div className='flex flex-col gap-8 w-fit h-fit items-center max-w-[1000px]'>
              <div className='flex w-fit items-center justify-center text-center text-gray-500 font-normal sm:text-[20px] text-[16px]'>
                {video.quote}
              </div>
              <div className='flex flex-col gap-2 w-fit items-center'>
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
          {index !== videos.length - 1 && (
            <SectionSeparator className='sm:mt-[80px] mt-[48px] sm:mb-[80px] mb-[64px]' />
          )}
        </div>
      ))}
    </div>
  );
}
