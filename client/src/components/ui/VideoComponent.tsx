import { PlayCircle20Regular } from '@fluentui/react-icons';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Dispatch, SetStateAction } from 'react';
import { Button } from '@/components/ui/Button';

type VideoComponentProps = {
  id: string;
  src: string;
  title: string;
  subtitle: string;
  buttonTitle: string;
  height: number;
  width: number;
  autoPlay?: boolean;
  isAutoPlayPaused?: boolean;
  isPlaying?: boolean;
  setIsPlaying?: Dispatch<SetStateAction<boolean>>;
};

export function VideoComponent(props: VideoComponentProps) {
  const {
    id,
    src,
    title,
    subtitle,
    buttonTitle,
    height,
    width,
    autoPlay = false,
    isAutoPlayPaused = false,
    isPlaying: externalIsPlaying,
    setIsPlaying: externalSetIsPlaying,
  } = props;

  const videoRef = useRef<HTMLVideoElement>(null);

  const [internalIsPlaying, setInternalIsPlaying] = useState(false);

  const handlePlay = useCallback(() => {
    if (videoRef.current) {
      videoRef.current.play();
      setInternalIsPlaying(true);
      externalSetIsPlaying?.(true);
    }
  }, [setInternalIsPlaying, externalSetIsPlaying]);

  const onCanPlay = useCallback(() => {
    if (autoPlay && videoRef.current && !isAutoPlayPaused) {
      videoRef.current.play();
      setInternalIsPlaying(true);
      externalSetIsPlaying?.(true);
    }
  }, [autoPlay, setInternalIsPlaying, externalSetIsPlaying, isAutoPlayPaused]);

  useEffect(() => {
    if (autoPlay && videoRef.current) {
      videoRef.current.load();
    }
  }, [src, autoPlay]);

  useEffect(() => {
    if (externalIsPlaying) {
      handlePlay();
    }
  }, [externalIsPlaying, handlePlay]);

  useEffect(() => {
    if (videoRef.current && autoPlay) {
      if (isAutoPlayPaused) {
        videoRef.current.pause();
      } else {
        videoRef.current?.play();
      }
    }
  }, [autoPlay, isAutoPlayPaused]);

  return (
    <div className='relative rounded-[12px]'>
      <video
        id={id}
        src={src}
        ref={videoRef}
        controls={internalIsPlaying && !autoPlay}
        height={height}
        width={width}
        playsInline
        className='object-cover rounded-[12px]'
        autoPlay={autoPlay && !isAutoPlayPaused}
        loop={autoPlay}
        onCanPlay={onCanPlay}
        muted={autoPlay}
      >
        <source src={src} type='video/mp4' />
      </video>

      {!internalIsPlaying && !autoPlay && (
        <div className='absolute inset-0 flex flex-col items-center justify-center bg-black bg-opacity-50 text-white rounded-[12px]'>
          <div className='text-2xl font-semibold mb-1'>{title}</div>
          <div className='font-normal mb-10 text-slate-200'>{subtitle}</div>
          <Button variant='outline' className='rounded-full text-medium text-black text-sm' onClick={handlePlay}>
            {buttonTitle} <PlayCircle20Regular />
          </Button>
        </div>
      )}
    </div>
  );
}
