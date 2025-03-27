import dayjs from 'dayjs';
import { cn } from '@/lib/utils';
import { useOrFetchFeedback } from '@/store';
import { TaskID, TenantID } from '@/types/aliases';
import { FeedbackItem } from '@/types/workflowAI';
import { Loader } from '../ui/Loader';

type FeedbackBoxProps = {
  feedbackList: FeedbackItem[] | undefined;
  isLoading: boolean | undefined;
};

export function FeedbackBox(props: FeedbackBoxProps) {
  const { feedbackList, isLoading } = props;

  return (
    <div className='bordered-box flex flex-col px-4'>
      <div className='bordered-box-title'>
        User Feedback
        {isLoading && <Loader className='ml-auto w-4 h-4' />}
      </div>

      {feedbackList?.map((feedback) => (
        <div className='bordered-box flex flex-col mb-2 max-h-28 overflow-y-auto' key={feedback.id}>
          <div className='flex flex-row items-center h-9 bg-gray-50 gap-1 px-3 flex-none'>
            <div
              className={cn(
                'capitalize text-sm font-bold',
                feedback.outcome === 'positive' ? 'text-green-500' : 'text-red-500'
              )}
            >
              {feedback.outcome}
            </div>
            ·<div className='text-sm font-normal text-gray-500'>{dayjs(feedback.created_at).format('MMM D, YYYY')}</div>
          </div>

          {feedback.comment && (
            <div className='px-4 py-3 text-gray-500 text-[13px] border-dashed border-t border-gray-200 whitespace-pre-line'>
              “{feedback.comment}”
            </div>
          )}
        </div>
      ))}

      {!isLoading && !feedbackList?.length && (
        <div className='flex flex-col items-center justify-center p-4'>No feedback yet</div>
      )}
    </div>
  );
}

type FeedbackBoxContainerProps = {
  tenant: TenantID | undefined;
  taskId: TaskID;
  taskRunId: string;
};

export function FeedbackBoxContainer(props: FeedbackBoxContainerProps) {
  const { tenant, taskId, taskRunId } = props;

  const { feedbackList, isLoading } = useOrFetchFeedback(tenant, taskId, taskRunId);

  return <FeedbackBox feedbackList={feedbackList} isLoading={isLoading} />;
}
