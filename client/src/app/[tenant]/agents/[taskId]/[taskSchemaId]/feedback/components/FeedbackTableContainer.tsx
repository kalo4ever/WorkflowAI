'use client';

import { ThumbLikeDislike16Filled } from '@fluentui/react-icons';
import { useCallback } from 'react';
import { EmptyContent } from '@/components/EmptyContent';
import TaskRunModal, { useRunIDParam } from '@/components/TaskRunModal/TaskRunModal';
import { Slack } from '@/components/icons/Slack';
import { Loader } from '@/components/ui/Loader';
import { PageContainer } from '@/components/v2/PageContainer';
import { useTaskSchemaParams } from '@/lib/hooks/useTaskParams';
import { cn } from '@/lib/utils';
import { useOrFetchFeedback, useOrFetchTask } from '@/store';
import { TaskID, TenantID } from '@/types/aliases';
import { FeedbackItem } from '@/types/workflowAI';
import { FeedbackHeader, FeedbackRow } from './FeedbackRow';

function FeedbackTable(props: {
  readonly tenant: TenantID;
  readonly taskId: TaskID;
  readonly className?: string;
  readonly setTaskRunId: (taskRunId: string | undefined) => void;
}) {
  const { tenant, taskId, className, setTaskRunId } = props;
  const { feedbackList, isLoading } = useOrFetchFeedback(tenant, taskId);

  const onFeedbackSelect = useCallback(
    (feedback: FeedbackItem) => {
      setTaskRunId(feedback.run_id);
    },
    [setTaskRunId]
  );

  if (isLoading) {
    return <Loader centered />;
  }

  if (!feedbackList?.length) {
    return (
      <EmptyContent
        icon={<ThumbLikeDislike16Filled />}
        title='No feedback yet'
        subtitle='To get started, add feedback buttons in your app in less than 3 minutes'
        buttonText='Get Started'
        href='https://docs.workflowai.com/features/user-feedback'
      />
    );
  }

  return (
    <div
      className={cn(
        className,
        'flex flex-col w-full h-full overflow-y-auto px-2 border rounded-[2px] border-gray-200 bg-gradient-to-b from-white/50 to-white/0'
      )}
    >
      <FeedbackHeader />
      {feedbackList?.map((feedbackItem) => {
        return <FeedbackRow key={feedbackItem.id} feedback={feedbackItem} onSelect={onFeedbackSelect} />;
      })}
    </div>
  );
}

function SlackIntegration() {
  return (
    <div className='flex flex-row bg-white border border-gray-200 px-4 py-3 gap-3 items-center'>
      <Slack className='w-5 h-5' />
      <div className='flex flex-col'>
        <div className='text-[13px] font-semibold'>Slack Integration (Coming Soon)</div>
        <div className='text-[13px] text-gray-500'>
          Send all new feedback to a Slack channel for better visibility and team collaboration.
        </div>
      </div>
    </div>
  );
}

export function FeedbackTableContainer() {
  const { tenant, taskId, taskSchemaId } = useTaskSchemaParams();
  const { task } = useOrFetchTask(tenant, taskId);
  const { taskRunId, setTaskRunId, clearTaskRunId } = useRunIDParam();

  return (
    <PageContainer task={task} name='User Feedback' showCopyLink={true} showSchema={false} isInitialized={!!task}>
      <div className='w-full h-full flex flex-col items-stretch gap-6 p-4'>
        <SlackIntegration />
        <FeedbackTable tenant={tenant} taskId={taskId} className='flex-1' setTaskRunId={setTaskRunId} />
        <TaskRunModal
          tenant={tenant}
          onClose={clearTaskRunId}
          open={!!taskRunId}
          taskId={taskId}
          taskRunId={taskRunId ?? ''}
          taskSchemaIdFromParams={taskSchemaId}
          showPlaygroundButton
        />
      </div>
    </PageContainer>
  );
}
