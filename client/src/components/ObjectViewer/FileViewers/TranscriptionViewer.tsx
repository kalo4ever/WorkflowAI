import { cx } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useCallback } from 'react';
import { useToggle } from 'usehooks-ts';
import { Button } from '@/components/ui/Button';

type TranscriptionViewerProps = {
  transcription: string | undefined;
  transcriptionLoading: boolean;
};

export function TranscriptionViewer(props: TranscriptionViewerProps) {
  const { transcription, transcriptionLoading } = props;
  const [showMore, toggleShowMore] = useToggle(false);
  const [isClamped, setIsClamped] = useState(false);
  const [transcriptionRef, setTranscriptionRef] = useState<HTMLSpanElement | null>(null);

  const handleResize = useCallback(() => {
    if (!transcriptionRef) return;
    if (transcriptionRef) {
      // We check if the line-clamp is active by comparing the height of the element
      // with the height of its content
      const contentHeight = transcriptionRef.scrollHeight;
      const elementHeight = transcriptionRef.clientHeight;
      const isClamped = contentHeight > elementHeight;
      setIsClamped(isClamped);
    }
  }, [transcriptionRef]);

  useEffect(() => {
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [handleResize]);

  const setRef = useCallback(
    (node: HTMLSpanElement) => {
      if (!node) return;
      setTranscriptionRef(node);
      handleResize();
    },
    [handleResize]
  );

  if (transcriptionLoading) {
    return (
      <div className='flex items-center gap-2'>
        <Loader2 size={16} className='animate-spin' />
        <span className='text-[13px] text-gray-900 font-normal'>Transcribing...</span>
      </div>
    );
  }

  if (!transcription) return null;

  return (
    <div className='flex flex-col gap-1 items-start'>
      <span
        ref={setRef}
        className={cx(
          'font-normal text-gray-900 text-[13px] break-words',
          showMore ? 'line-clamp-none max-h-[100px] overflow-y-auto' : 'line-clamp-2'
        )}
      >
        {transcription}
      </span>
      {isClamped && (
        <Button variant='text' onClick={toggleShowMore} className='p-0 h-fit text-[13px] text-gray-900 font-medium'>
          {showMore ? 'Show less' : 'Show more'}
        </Button>
      )}
    </div>
  );
}
