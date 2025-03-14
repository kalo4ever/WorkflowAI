import { ArrowClockwise16Regular } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';
import dayjs from 'dayjs';
import { WORKFLOW_AI_USERNAME } from '@/lib/constants';
import { WorkflowAIIcon } from '../Logos/WorkflowAIIcon';
import { Avatar, AvatarImage } from '../ui/Avatar/Avatar';
import { Button } from '../ui/Button';

export type ConversationMessage = {
  message: string | React.ReactNode;
  username: string;
  date?: Date;
  imageUrl?: string;
  streamed?: boolean;
};

type MessageAvatarProps = {
  imageUrl?: string | undefined;
  username: string;
};

function MessageAvatar(props: MessageAvatarProps) {
  const { imageUrl, username } = props;

  if (imageUrl) {
    return (
      <Avatar className='h-8 w-8'>
        <AvatarImage src={imageUrl} />
      </Avatar>
    );
  }

  return (
    <div className='w-8 h-8 flex items-center justify-center rounded-full border border-gray-200 shrink-0'>
      {username === WORKFLOW_AI_USERNAME ? (
        <WorkflowAIIcon className='shrink-0' />
      ) : (
        username[0].toUpperCase()
      )}
    </div>
  );
}

type TaskConversationRetryCellProps = {
  retry: () => void;
};

export function TaskConversationRetryCell(
  props: TaskConversationRetryCellProps
) {
  const { retry } = props;

  return (
    <div className='flex w-full gap-3 pt-2 pb-3 border-gray-200 overflow-hidden shrink-0'>
      <MessageAvatar imageUrl={undefined} username={WORKFLOW_AI_USERNAME} />
      <div className='flex-1 flex w-full flex-col gap-1 overflow-hidden font-lato'>
        <div className='w-full flex pt-1 gap-2 items-center justify-between'>
          <span className='font-semibold text-gray-700 text-base'>
            {WORKFLOW_AI_USERNAME}
          </span>
        </div>
        <div className='flex flex-row gap-2 w-fit items-center'>
          <div className='flex-1 text-sm text-gray-500 whitespace-break-spaces'>
            Something went wrong.
          </div>
          <Button
            variant='newDesignGray'
            onClick={retry}
            size='sm'
            icon={<ArrowClockwise16Regular />}
            className='bg-gray-200/70 hover:bg-gray-300/70'
          >
            Try Again
          </Button>
        </div>
      </div>
    </div>
  );
}

type TaskConversationMessageProps = {
  message: ConversationMessage;
  isLast?: boolean;
};

export function TaskConversationMessage(props: TaskConversationMessageProps) {
  const { message, isLast } = props;

  return (
    <div
      className={cx(
        'flex w-full gap-3 pt-2 pb-3 border-b border-gray-200 overflow-hidden shrink-0',
        isLast && 'border-b-0'
      )}
    >
      <MessageAvatar imageUrl={message.imageUrl} username={message.username} />
      <div className='flex-1 flex w-full flex-col gap-1 overflow-hidden font-lato'>
        <div className='w-full flex pt-1 gap-2 items-center justify-between'>
          <span className='font-semibold text-gray-700 text-base'>
            {message.username}
          </span>
          {message.date && (
            <span className='text-sm text-center text-gray-500 font-normal'>
              {dayjs(message.date).fromNow()}
            </span>
          )}
        </div>
        <div className='flex-1 text-sm text-gray-700 whitespace-break-spaces'>
          {message.message}
        </div>
      </div>
    </div>
  );
}
