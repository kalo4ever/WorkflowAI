import { cx } from 'class-variance-authority';
import { LoadingSuggestedDepartmentEntry } from './Loading/LoadingSuggestedDepartmentEntry';
import { SectionEntry } from './SuggestedAgentsSection';

type SuggestedDepartmentEntryProps = {
  entry: SectionEntry;
  isSelected: boolean;
  onClick: () => void;
};

export function SuggestedDepartmentEntry(props: SuggestedDepartmentEntryProps) {
  const { entry, isSelected, onClick } = props;

  return (
    <div
      className={cx(
        'flex flex-shrink-0 px-4 py-2 items-center justify-center cursor-pointer rounded-[2px] font-semibold text-[13px] capitalize',
        isSelected
          ? 'text-gray-50 bg-gray-800'
          : 'text-gray-800 bg-gray-100 hover:bg-gray-200'
      )}
      onClick={onClick}
    >
      {entry.department ?? 'All'}
    </div>
  );
}

type SuggestedDepartmentEntriesProps = {
  entries: SectionEntry[];
  selectedDepartment: string | undefined;
  setSelectedDepartment: (department: string | undefined) => void;
  inProgress: boolean;
  isStreamingAgents: boolean;
};

export function SuggestedDepartmentEntries(
  props: SuggestedDepartmentEntriesProps
) {
  const {
    entries,
    selectedDepartment,
    setSelectedDepartment,
    inProgress,
    isStreamingAgents,
  } = props;

  if (inProgress) {
    return (
      <div className='flex flex-wrap gap-2 px-5 pb-4 items-center justify-start animate-pulse'>
        {[...Array(4)].map((_, i) => (
          <LoadingSuggestedDepartmentEntry key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className='flex flex-wrap gap-2 px-5 pb-4 items-center justify-start'>
      {entries.map((entry) => (
        <SuggestedDepartmentEntry
          key={entry.department ?? 'all'}
          entry={entry}
          isSelected={entry.department === selectedDepartment}
          onClick={() => setSelectedDepartment(entry.department)}
        />
      ))}
      {isStreamingAgents && (
        <div className='animate-pulse'>
          <LoadingSuggestedDepartmentEntry />
        </div>
      )}
    </div>
  );
}
