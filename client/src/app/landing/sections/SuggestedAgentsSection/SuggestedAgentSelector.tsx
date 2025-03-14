import { ShareRegular } from '@fluentui/react-icons';
import { useMemo } from 'react';
import { Button } from '@/components/ui/Button';
import { useCopyCurrentUrl } from '@/lib/hooks/useCopy';
import { SuggestedAgent } from '@/store/suggested_agents';
import { CompanyURLEditor } from './CompanyURLEditor';
import { SuggestedAgentEntries } from './SuggestedAgentEntry';
import { SectionEntry } from './SuggestedAgentsSection';
import { SuggestedDepartmentEntries } from './SuggestedDepartmentEntry';

type SuggestedAgentSelectorProps = {
  companyURL: string | undefined;
  entries: SectionEntry[];
  selectedDepartment: string | undefined;
  setSelectedDepartment: (department: string | undefined) => void;
  showShareButton: boolean;
  showInternalScrollForAgents: boolean;
  showEditButton: boolean;
  inProgress: boolean;
  isStreamingAgents: boolean;
};

export function SuggestedAgentSelector(props: SuggestedAgentSelectorProps) {
  const {
    companyURL,
    entries,
    selectedDepartment,
    setSelectedDepartment,
    showShareButton,
    showEditButton,
    showInternalScrollForAgents,
    inProgress,
    isStreamingAgents,
  } = props;

  const agentsForSelectedDepartment: SuggestedAgent[] | undefined =
    useMemo(() => {
      return entries.find((entry) => entry.department === selectedDepartment)
        ?.agents;
    }, [entries, selectedDepartment]);

  const onCopy = useCopyCurrentUrl();

  return (
    <div className='flex flex-col pt-6 overflow-hidden w-full'>
      <div className='flex flex-row justify-between items-center px-5 pb-6'>
        {!!companyURL && (
          <CompanyURLEditor
            companyURL={companyURL}
            supportEditing={showEditButton}
          />
        )}
        {!!showShareButton && (
          <Button
            variant='newDesign'
            onClick={onCopy}
            icon={<ShareRegular className='h-4 w-4 text-gray-800' />}
            size='none'
            className='py-2 px-3'
          >
            Share
          </Button>
        )}
      </div>
      <SuggestedDepartmentEntries
        entries={entries}
        selectedDepartment={selectedDepartment}
        setSelectedDepartment={setSelectedDepartment}
        inProgress={inProgress}
        isStreamingAgents={isStreamingAgents}
      />
      <SuggestedAgentEntries
        agents={agentsForSelectedDepartment}
        showInternalScrollForAgents={showInternalScrollForAgents}
        companyURL={companyURL}
        inProgress={inProgress}
        isStreamingAgents={isStreamingAgents}
      />
    </div>
  );
}
