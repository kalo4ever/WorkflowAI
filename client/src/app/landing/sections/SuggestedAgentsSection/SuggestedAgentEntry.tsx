import { cx } from 'class-variance-authority';
import dayjs from 'dayjs';
import { Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useCallback, useMemo, useState } from 'react';
import { HoverCard, HoverCardContent } from '@/components/ui/HoverCard';
import { HoverCardTrigger } from '@/components/ui/HoverCard';
import { useLoggedInTenantID } from '@/lib/hooks/useTaskParams';
import { taskSchemaRoute } from '@/lib/routeFormatter';
import {
  SuggestedAgent,
  buildSuggestedAgentPreviewScopeKey,
  useSuggestedAgentPreview,
} from '@/store/suggested_agents';
import { useTasks } from '@/store/task';
import { JsonSchema } from '@/types';
import { TaskID, TaskSchemaID } from '@/types/aliases';
import { CreateTaskRequest } from '@/types/workflowAI';
import { LoadingSuggestedAgentEntry } from './Loading/LoadingSuggestedAgentEntry';
import { SuggestedAgentDetailsTooltip } from './SuggestedAgentDetailsTooltip';

export type SuggestedAgentEntryProps = {
  agent: SuggestedAgent;
  companyURL?: string;
};

export function SuggestedAgentEntry(props: SuggestedAgentEntryProps) {
  const { agent, companyURL } = props;

  const scopeKey = buildSuggestedAgentPreviewScopeKey({ agent });

  const preview = useSuggestedAgentPreview((state) =>
    !!scopeKey ? state.previewByScope.get(scopeKey) : undefined
  );

  const previewInProgress = useSuggestedAgentPreview((state) =>
    !!scopeKey ? state.isLoadingByScope.get(scopeKey) : false
  );

  const router = useRouter();

  const inputSchema = preview?.agent_input_schema as JsonSchema;
  const outputSchema = preview?.agent_output_schema as JsonSchema;

  const loggedInTenant = useLoggedInTenantID();
  const createTask = useTasks((state) => state.createTask);

  const [creatingTaskInProgress, setCreatingTaskInProgress] = useState(false);

  const onCreateAgent = useCallback(async () => {
    if (
      !inputSchema ||
      !outputSchema ||
      previewInProgress ||
      creatingTaskInProgress
    ) {
      return;
    }
    setCreatingTaskInProgress(true);

    const payload: CreateTaskRequest = {
      chat_messages: [],
      name:
        agent?.agent_description ??
        `AI agent ${dayjs().format('YYYY-MM-DD-HH-mm-ss')}`,
      input_schema: inputSchema as Record<string, unknown>,
      output_schema: outputSchema as Record<string, unknown>,
    };

    const task = await createTask(loggedInTenant, payload);
    const route = taskSchemaRoute(
      loggedInTenant,
      task.id as TaskID,
      `${task.schema_id}` as TaskSchemaID,
      {
        companyURL: companyURL?.toLowerCase(),
      }
    );

    router.push(route);

    setTimeout(() => {
      setCreatingTaskInProgress(false);
    }, 4000);
  }, [
    inputSchema,
    outputSchema,
    loggedInTenant,
    createTask,
    agent,
    router,
    setCreatingTaskInProgress,
    companyURL,
    previewInProgress,
    creatingTaskInProgress,
  ]);

  const badgeText = useMemo(() => {
    if (creatingTaskInProgress) {
      return 'Building Agent';
    }

    return undefined;
  }, [creatingTaskInProgress]);

  return (
    <HoverCard>
      <HoverCardTrigger asChild>
        <div
          className={
            'flex flex-col gap-1 cursor-pointer rounded-[4px] text-start p-4 justify-between border hover:border-gray-300 hover:bg-gray-300 border-gray-200 bg-white'
          }
          onClick={onCreateAgent}
        >
          <div className='flex flex-col w-full items-start justify-center'>
            {!!badgeText && (
              <div className='flex flex-row gap-2 items-center justify-start pb-2'>
                <div
                  className={
                    'text-[13px] font-medium text-white px-2 py-1 bg-indigo-500 rounded-[4px] flex flex-row gap-2 items-center justify-center'
                  }
                >
                  <Loader2 className='h-[14px] w-[14px] animate-spin text-white' />
                  <div>{badgeText}</div>
                </div>
              </div>
            )}
            <div className={'text-[12px] font-medium text-gray-500'}>
              {agent.agent_description}
            </div>
            <div className={'text-[16px] font-semibold text-gray-700 pt-[4px]'}>
              {agent.explanation}
            </div>
          </div>
          <div className='flex flex-row gap-2 items-center justify-start pt-2'>
            <div
              className={
                'text-[13px] font-medium text-gray-700 px-[6px] py-1 bg-gray-200 rounded-[2px] capitalize'
              }
            >
              {agent.department}
            </div>
          </div>
        </div>
      </HoverCardTrigger>
      <HoverCardContent
        className='flex w-full m-1 p-0 border-gray-300 bg-custom-gradient-1 max-h-[min(572px,80vh)] max-w-[min(750px,47vw)] overflow-hidden'
        side={'right'}
      >
        <SuggestedAgentDetailsTooltip preview={preview} />
      </HoverCardContent>
    </HoverCard>
  );
}

type SuggestedAgentEntriesProps = {
  agents: SuggestedAgent[] | undefined;
  showInternalScrollForAgents: boolean;
  companyURL: string | undefined;
  inProgress: boolean;
  isStreamingAgents: boolean;
};

export function SuggestedAgentEntries(props: SuggestedAgentEntriesProps) {
  const {
    agents,
    showInternalScrollForAgents,
    companyURL,
    inProgress,
    isStreamingAgents,
  } = props;

  if (inProgress) {
    return (
      <div
        className={cx(
          'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 px-5 pb-4',
          showInternalScrollForAgents && 'overflow-y-auto'
        )}
      >
        {[...Array(9)].map((_, i) => (
          <LoadingSuggestedAgentEntry key={i} />
        ))}
      </div>
    );
  }

  return (
    <div
      className={cx(
        'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 px-5 pb-4',
        showInternalScrollForAgents && 'overflow-y-auto'
      )}
    >
      {agents?.map((agent) => (
        <SuggestedAgentEntry
          key={agent.agent_description}
          agent={agent}
          companyURL={companyURL}
        />
      ))}
      {isStreamingAgents && <LoadingSuggestedAgentEntry />}
    </div>
  );
}
