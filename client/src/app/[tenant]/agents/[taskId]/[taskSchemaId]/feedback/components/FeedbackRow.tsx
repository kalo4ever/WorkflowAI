import dayjs from 'dayjs';
import { cn } from '@/lib/utils';
import { FeedbackItem } from '@/types/workflowAI';

export function FeedbackHeader() {
  return (
    <div className='flex flex-row text-sm font-bold w-full border-b border-gray-200/60 text-[13px] text-gray-700 h-10'>
      <div className='flex-none  w-[69px] text-left flex items-center justify-center capitalize'>Review</div>
      <div className='flex-none text-left w-[120px] pl-2 flex items-center'>Date</div>
      <div className='flex-1 text-left pl-2 flex items-center'>Comment</div>
    </div>
  );
}

export function FeedbackRow(props: { feedback: FeedbackItem; onSelect: (feedback: FeedbackItem) => void }) {
  const { feedback, onSelect } = props;

  return (
    <div
      className='flex flex-row w-full border-b last:border-b-0 border-gray-200/60 text-[13px] text-gray-700 items-center h-11 cursor-pointer'
      onClick={() => onSelect(feedback)}
    >
      <div
        className={cn(
          'flex-none text-sm font-bold w-[69px] text-left flex pl-2 capitalize pb-px',
          feedback.outcome === 'positive' ? 'text-green-600' : 'text-red-500'
        )}
      >
        {feedback.outcome}
      </div>
      <div className='flex-none text-left w-[120px] pl-2 flex text-xs text-gray-500'>
        {dayjs(feedback.created_at).format('MMM D, YYYY')}
      </div>
      <div className='flex-1 text-left pl-2 flexjustify-center text-xs text-gray-500 flex items-center min-w-0'>
        <span className='truncate'>{feedback.comment && `“${feedback.comment}”`}</span>
      </div>
    </div>
  );
}
