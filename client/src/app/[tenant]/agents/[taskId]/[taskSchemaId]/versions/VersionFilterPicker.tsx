import { cx } from 'class-variance-authority';
import { useMemo } from 'react';
import { SimpleTooltip } from '@/components/ui/Tooltip';
import { TaskSchemaID } from '@/types/aliases';

type VersionFilterPickerButtonProps = {
  title?: string;
  isSelected: boolean;
  onClick: () => void;
};

export function VersionFilterPickerButton(props: VersionFilterPickerButtonProps) {
  const { title, isSelected, onClick } = props;
  return (
    <div
      className={cx(
        'py-1 rounded-[2px] text-[13px] text-gray-500 cursor-pointer px-2 font-lato border hover:text-gray-800',
        isSelected && !!title ? 'bg-white border-gray-300 text-gray-800 shadow-sm' : 'border-transparent',
        isSelected && !title && 'text-gray-800'
      )}
      onClick={onClick}
    >
      {!!title && title}
    </div>
  );
}

type VersionFilterPickerProps = {
  schema_id: TaskSchemaID;
  numberOfAllVersions: number;
  numberOfDeployedVersions: number;
  numberOfFavoriteVersions: number;
  filterOption: 'deployed' | 'favorite' | undefined;
  setFilterOption: (filterOption: 'deployed' | 'favorite' | undefined) => void;
};

type VersionFilterPickerEntry = {
  title: string;
  tooltipText: string;
  filterOption: 'deployed' | 'favorite' | undefined;
};

export function VersionFilterPicker(props: VersionFilterPickerProps) {
  const {
    schema_id,
    numberOfAllVersions,
    numberOfDeployedVersions,
    numberOfFavoriteVersions,
    filterOption,
    setFilterOption,
  } = props;

  const options: VersionFilterPickerEntry[] = useMemo(() => {
    const options: VersionFilterPickerEntry[] = [];

    if (numberOfAllVersions > 0) {
      options.push({
        title: `All (${numberOfAllVersions})`,
        tooltipText: `View all versions on Schema #${schema_id}`,
        filterOption: undefined,
      });
    }

    if (numberOfDeployedVersions > 0) {
      options.push({
        title: `Deployed (${numberOfDeployedVersions})`,
        tooltipText: 'View only deployed versions',
        filterOption: 'deployed',
      });
    }

    if (numberOfFavoriteVersions > 0) {
      options.push({
        title: `Favorite (${numberOfFavoriteVersions})`,
        tooltipText: 'View only favorited versions',
        filterOption: 'favorite',
      });
    }

    return options;
  }, [numberOfAllVersions, numberOfDeployedVersions, numberOfFavoriteVersions, schema_id]);

  if (options.length === 0 || options.length === 1) {
    return null;
  }

  return (
    <div className='flex flex-row p-1 rounded-[2px] border border-gray-300 items-center'>
      {options.map((option) => (
        <SimpleTooltip
          key={option.title}
          content={<div className='whitespace-break-spaces text-center'>{option.tooltipText}</div>}
        >
          <div>
            <VersionFilterPickerButton
              title={option.title}
              isSelected={filterOption === option.filterOption}
              onClick={() => setFilterOption(option.filterOption)}
            />
          </div>
        </SimpleTooltip>
      ))}
    </div>
  );
}
