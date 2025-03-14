import { useCallback, useMemo, useState } from 'react';
import { TaskConversationInput } from '@/components/NewTaskModal/TaskConversation';
import { TaskConversationMessages } from '@/components/NewTaskModal/TaskConversation';
import { ConversationMessage } from '@/components/NewTaskModal/TaskConversationMessage';
import { SuggestedAgentsChatMessage } from '@/store/suggested_agents';
import { useSuggestedAgents } from '@/store/suggested_agents';
import { capitalizeCompanyURL } from '../untils';

type ChatSectionProps = {
  companyURL: string;
  messages: SuggestedAgentsChatMessage[] | undefined;
  inProgress: boolean;
};

export function ChatSection(props: ChatSectionProps) {
  const { companyURL, messages, inProgress } = props;

  const convertedMessages: ConversationMessage[] = useMemo(() => {
    const mappedMessages =
      messages?.map((message, index) => ({
        message: message.content_str,
        username: message.role === 'USER' ? 'You' : 'WorkflowAI',
        streamed:
          message.role === 'ASSISTANT' &&
          index === messages.length - 1 &&
          inProgress,
      })) ?? [];

    const firstMessage: ConversationMessage = {
      message: capitalizeCompanyURL(companyURL),
      username: 'You',
      streamed: false,
    };

    return mappedMessages.length > 0
      ? [firstMessage, ...mappedMessages.slice(1)]
      : [firstMessage];
  }, [messages, inProgress, companyURL]);

  const [userMessage, setUserMessage] = useState('');

  const sendMessage = useSuggestedAgents((state) => state.sendMessage);

  const onSendIteration = useCallback(async () => {
    if (userMessage) {
      const message = userMessage;
      setUserMessage('');
      await sendMessage(companyURL, message);
    }
  }, [companyURL, sendMessage, userMessage]);

  return (
    <div className='flex flex-col w-[272px] min-w-[272px] flex-1 h-full pt-3 text-start border-l border-gray-100 bg-white shadow-[0_20px_25px_-5px_rgba(0,0,0,0.05)] overflow-hidden'>
      <TaskConversationMessages
        messages={convertedMessages}
        loading={inProgress}
        showRetry={false}
        retry={() => {}}
      />
      <TaskConversationInput
        setUserMessage={setUserMessage}
        onSendIteration={onSendIteration}
        userMessage={userMessage}
        autoFocus={false}
      />
    </div>
  );
}
