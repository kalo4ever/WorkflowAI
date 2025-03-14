import { cx } from 'class-variance-authority';
import { useEffect, useMemo, useState } from 'react';
import { useOrFetchSuggestedAgentsIfNeeded } from '@/store/fetchers';
import {
  SuggestedAgent,
  useSuggestedAgentPreview,
} from '@/store/suggested_agents';
import { ChatSection } from '../ChatSection/ChatSection';
import { SuggestedAgentSelector } from './SuggestedAgentSelector';

export type SectionEntry = {
  department: string | undefined;
  agents: SuggestedAgent[];
};

type SuggestedAgentsSectionProps = {
  className?: string;
  companyURL: string;
  landingPageMode?: boolean;
};

export function SuggestedAgentsSection(props: SuggestedAgentsSectionProps) {
  const { className, companyURL, landingPageMode = true } = props;

  const {
    suggestedAgents,
    streamedAgents,
    isLoading: inProgress,
    messages,
  } = useOrFetchSuggestedAgentsIfNeeded(companyURL);

  const { fetchSuggestedTaskPreviewIfNeeded } = useSuggestedAgentPreview();

  useEffect(() => {
    if (!suggestedAgents || suggestedAgents.length === 0) {
      return;
    }

    suggestedAgents.forEach((agent) => {
      fetchSuggestedTaskPreviewIfNeeded(agent);
    });
  }, [suggestedAgents, fetchSuggestedTaskPreviewIfNeeded]);

  const agents = useMemo(() => {
    if (!!suggestedAgents && suggestedAgents.length > 0) {
      return suggestedAgents;
    }

    if (!!streamedAgents && streamedAgents.length > 0) {
      return streamedAgents;
    }

    return undefined;
  }, [suggestedAgents, streamedAgents]);

  const agentsPerDepartment: SectionEntry[] = useMemo(() => {
    const result: SectionEntry[] = [];

    if (agents) {
      result.push({
        department: undefined,
        agents: agents,
      });
    }

    agents?.forEach((agent) => {
      const department = agent.department;
      const existingDepartment = result.find(
        (item) => item.department === department
      );

      if (existingDepartment) {
        existingDepartment.agents.push(agent);
      } else {
        result.push({
          department,
          agents: [agent],
        });
      }
    });

    return result;
  }, [agents]);

  const [selectedDepartment, setSelectedDepartment] = useState<
    string | undefined
  >(undefined);

  useEffect(() => {
    if (!!selectedDepartment) {
      return;
    }

    if (agentsPerDepartment.length > 0) {
      setSelectedDepartment(agentsPerDepartment[0].department);
    }
  }, [agentsPerDepartment, selectedDepartment]);

  const isStreamingAgents = !!streamedAgents && streamedAgents.length > 0;

  return (
    <div
      className={cx(
        'flex flex-row w-full',
        landingPageMode
          ? 'bg-white/70 border border-gray-200 shadow-md rounded-[4px] overflow-hidden min-h-[700px]'
          : 'h-full overflow-hidden',
        className
      )}
    >
      <SuggestedAgentSelector
        companyURL={companyURL}
        entries={agentsPerDepartment}
        selectedDepartment={selectedDepartment}
        setSelectedDepartment={setSelectedDepartment}
        showShareButton={landingPageMode}
        showInternalScrollForAgents={!landingPageMode}
        showEditButton={landingPageMode}
        inProgress={inProgress && !isStreamingAgents}
        isStreamingAgents={isStreamingAgents}
      />
      <div className='flex-1 min-w-[272px] h-[inherit] relative'>
        <div className='absolute inset-0 overflow-hidden'>
          <ChatSection
            companyURL={companyURL}
            messages={messages}
            inProgress={inProgress}
          />
        </div>
      </div>
    </div>
  );
}
