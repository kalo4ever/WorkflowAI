import {
  ArrowCircleUp28Filled,
  ArrowCircleUp28Regular,
} from '@fluentui/react-icons';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Textarea } from '@/components/ui/Textarea';
import { WORKFLOW_AI_USERNAME } from '@/lib/constants';
import { cn } from '@/lib/utils';
import { WorkflowAIGradientIcon } from '../Logos/WorkflowAIIcon';
import { JumpingDotsLoader } from './JumpingDotsLoader';
import {
  ConversationMessage,
  TaskConversationMessage,
  TaskConversationRetryCell,
} from './TaskConversationMessage';

dayjs.extend(relativeTime);

const DEFAULT_MESSAGE_SUGGESTIONS = [
  'Given a product review, extract the main sentiment.',
  'Extract the city and country from the image.',
  'Summarize a text.',
];

type TaskConversationInputProps = {
  userMessage: string;
  setUserMessage: (message: string) => void;
  onSendIteration: () => Promise<void>;
  autoFocus?: boolean;
};

export function TaskConversationInput(props: TaskConversationInputProps) {
  const {
    userMessage,
    setUserMessage,
    onSendIteration,
    autoFocus = true,
  } = props;
  const [isFocused, setIsFocused] = useState(false);

  const onMessageChange = useCallback(
    (event: React.ChangeEvent<HTMLTextAreaElement>) => {
      setUserMessage(event.target.value);
    },
    [setUserMessage]
  );

  const onKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        onSendIteration();
      }
    },
    [onSendIteration]
  );

  const sendDisabled = !userMessage;

  return (
    <div className='flex w-full h-fit p-4'>
      <div
        className={cn(
          'flex flex-row w-full h-fit justify-between items-end bg-white rounded-[2px] border border-gray-300 border-input',
          isFocused
            ? 'border-[2px] border-gray-900 -m-[1px]'
            : 'border-[1px] border-gray-200'
        )}
      >
        <Textarea
          value={userMessage}
          onChange={onMessageChange}
          placeholder='Type your message here...'
          className='max-h-[300px] font-lato text-sm text-gray-900 border-none focus-visible:ring-0 focus:outline-none scrollbar-hide'
          onKeyDown={onKeyDown}
          autoFocus={autoFocus}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
        />

        {sendDisabled ? (
          <ArrowCircleUp28Regular className='text-gray-300 cursor-not-allowed mx-2 my-2' />
        ) : (
          <ArrowCircleUp28Filled
            className='text-indigo-600 cursor-pointer mx-2 my-2'
            onClick={!sendDisabled ? () => onSendIteration() : undefined}
          />
        )}
      </div>
    </div>
  );
}

type TaskConversationMessagesProps = {
  messages: ConversationMessage[];
  loading: boolean;
  showRetry: boolean;
  retry: () => void;
};

export function TaskConversationMessages(props: TaskConversationMessagesProps) {
  const { messages, loading, showRetry, retry } = props;
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [loading, messages]);

  const isStreaming = useMemo(
    () => messages.some((message) => message.streamed),
    [messages]
  );

  return (
    <div ref={scrollRef} className='flex flex-col flex-1 overflow-y-auto px-4'>
      {messages.map((message, index) => (
        <TaskConversationMessage
          key={!!message.date ? dayjs(message.date).format() : index}
          message={message}
          isLast={message === messages[messages.length - 1]}
        />
      ))}
      {showRetry && <TaskConversationRetryCell retry={retry} />}
      {loading && !isStreaming && (
        <TaskConversationMessage
          message={{
            username: WORKFLOW_AI_USERNAME,
            message: <JumpingDotsLoader />,
          }}
          isLast
        />
      )}
      {isStreaming && <JumpingDotsLoader className='pl-10 pt-1' />}
    </div>
  );
}

type TaskConversationMessageSuggestionProps = {
  suggestion: string;
  onSendIteration: (suggestion?: string) => Promise<void>;
};

function TaskConversationMessageSuggestion(
  props: TaskConversationMessageSuggestionProps
) {
  const { suggestion, onSendIteration } = props;

  const onClick = useCallback(() => {
    onSendIteration(suggestion);
  }, [onSendIteration, suggestion]);

  return (
    <div
      className='w-[240px] border border-gray-300 bg-white font-normal text-base rounded-[2px] p-4 text-gray-600 hover:bg-gray-100 cursor-pointer transition-colors'
      onClick={onClick}
    >
      {suggestion}
    </div>
  );
}

type TaskConverationGreetingProps = {
  userFirstName?: string | undefined | null;
  onSendIteration: (suggestion?: string) => Promise<void>;
};

function TaskConverationGreeting(props: TaskConverationGreetingProps) {
  const { userFirstName, onSendIteration } = props;
  const greetingMessage = useMemo(
    () =>
      `Hi${userFirstName ? ` ${userFirstName}` : ''}, what do you want to build today?`,
    [userFirstName]
  );
  return (
    <div className='flex-1 flex flex-col justify-center items-center font-lato'>
      <WorkflowAIGradientIcon ratio={3.4} />
      <div className='pt-8 text-center text-gray-700 text-lg font-medium'>
        {greetingMessage}
      </div>
      <div className='pt-8 flex gap-3 items-center'>
        {DEFAULT_MESSAGE_SUGGESTIONS.map((suggestion, index) => (
          <TaskConversationMessageSuggestion
            key={index}
            suggestion={suggestion}
            onSendIteration={onSendIteration}
          />
        ))}
      </div>
    </div>
  );
}

type TaskConversationProps = TaskConversationMessagesProps &
  TaskConversationInputProps & {
    userFirstName?: string | undefined | null;
  };

export function TaskConversation(props: TaskConversationProps) {
  const {
    userMessage,
    messages,
    loading,
    userFirstName,
    setUserMessage,
    onSendIteration,
    showRetry,
    retry,
  } = props;

  return (
    <div className='flex flex-col h-full'>
      {messages.length === 0 ? (
        <TaskConverationGreeting
          userFirstName={userFirstName}
          onSendIteration={onSendIteration}
        />
      ) : (
        <TaskConversationMessages
          messages={messages}
          loading={loading}
          showRetry={showRetry}
          retry={retry}
        />
      )}
      <TaskConversationInput
        setUserMessage={setUserMessage}
        onSendIteration={onSendIteration}
        userMessage={userMessage}
      />
    </div>
  );
}
